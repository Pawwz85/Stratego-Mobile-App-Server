from __future__ import annotations

import collections
from typing import Callable
import uuid

from src.Core.JobManager import JobManager, Job, DelayedTask
from src.Core.User import User
from src.Core.stratego_gamestate import Side
from src.Core.table import Table, TableApi, TableGamePhase
from src.Core.chat import Chat, ChatApi
from src.Events.Events import EventLogicalEndpointWithSignature, Eventmanager


class Room:
    """
     Represents a room where users can join, interact, and participate in events.
     This class manages users, broadcasts events, and handles room termination.

     Attributes:
         users (dict[int, User]): A dictionary mapping user IDs to User objects within the room.
         user_list_updates (int): A counter tracking the number of user list updates.
         job_manager (JobManager): Manages jobs and tasks associated with the room.
         __mark_self_for_deletion (Callable[[str], any]): Callback function to mark the room for deletion.
         _table (Table): The table associated with the room, handling seat changes and events.
         _chat (Chat): Chat system associated with the room for user communication.
         _password (str): Password for room access (optional).
         _job (Job or None): Job object associated with the room, if any.
         _inactive_room_auto_termination (DelayedTask or None): Task to automatically terminate the room if inactive.
         _id (str): Unique identifier for the room.
         event_manager (EventManager): Manages event distribution within the room.
     """
    class Builder:
        """
        Builder is a fluent interface class that allows the construction of a Room object by setting various
        attributes and callback functions on the Builder instance. The Room object will be created by calling the
        `build()` method on the Builder instance.

        Attributes: - job_manager (JobManager): A reference to the JobManager instance used for scheduling tasks -
        event_manager (Eventmanager): An instance of the Eventmanager class, responsible for managing events in the
        room - table_builder (Table.Builder): The Builder object for constructing a Table object inside the Room -
        chat (Chat): A Chat object to store messages and facilitate messaging between users inside the Room -
        password: Optional password for the Room, which will be enforced during user authentication

        """
        def __init__(self, job_manager: JobManager, mark_for_deletion: Callable[[str], any]):
            self.job_manager = job_manager
            self.event_manager: Eventmanager = Eventmanager(job_manager)
            self.table_builder = Table.Builder(job_manager)
            self.chat_cap = 1024
            self.password: str | None = None
            self.mark_for_deletion: Callable = mark_for_deletion

        def set_table_builder(self, table_builder: Table.Builder):
            """
            Sets the Table Builder object used to construct a Table object inside the Room. The Builder instance for
            the Table object can be customized by implementing its own methods.

            :param table_builder: The Table Builder object to set as the builder for the Room's Table
            :return: The Builder object, allowing method chaining
            """
            self.table_builder = table_builder
            return self

        def set_chat_cap(self, size: int):
            """
            Sets the maximum chat message capacity in messages. This attribute will be passed to the Chat object
            during its construction inside the Room.

            :param size: The maximum chat message capacity in messages
            :return: The Builder object, allowing method chaining
            """
            self.chat_cap = size
            return self

        def set_password(self, password: str | None):
            """
            Sets an optional password for the Room, which will be needed by users to join.

            :param password: The password for the Room (optional)
            :return: The Builder object, allowing method chaining
            """
            self.password = password
            return self

        def set_event_manager(self, event_manager: Eventmanager):
            """
            Sets an instance of the Eventmanager class to manage events inside the Room. This attribute will be
            passed to the Eventmanager during its construction.

            :param event_manager: The Eventmanager object for managing events inside the Room
            :return: The Builder object, allowing method chaining
            """
            self.event_manager = event_manager
            return self

        def build(self) -> Room:
            """
            Creates a new Room instance using the attributes and callback functions set on the Builder object. This
            method should be called after all customization has been completed.

            :return: The newly created Room object
            """
            result: Room = Room(self.job_manager, self.event_manager, self.table_builder, self.mark_for_deletion)
            result._chat = Chat(result.event_broadcast, self.chat_cap)
            result._password = self.password
            return result

    def __init__(self, job_manager: JobManager, event_manager: Eventmanager,
                 table_builder: Table.Builder, mark_for_deletion: Callable[[str], any]):
        """
              Initializes the Room instance with the provided job manager, event manager, and table builder.

              :param job_manager: An instance of JobManager for managing jobs and tasks in the room.
              :param event_manager: An instance of EventManager for managing event distribution.
              :param table_builder: A Table.Builder object for constructing the table associated with the room.
              :param mark_for_deletion: A callable that marks the room for deletion when invoked.
              :return: None
        """
        self.users: dict[int, User] = dict()
        self.user_list_updates = 0
        self.job_manager = job_manager
        self.__mark_self_for_deletion = mark_for_deletion
        self._table = (table_builder.
                       set_seat_observer(self.__on_seat_change).
                       set_event_channels({None: self.__spectator_channel,
                                           Side.blue: lambda body: self.__players_channel(body, Side.blue),
                                           Side.red: lambda body: self.__players_channel(body, Side.red)}).
                       set_event_broadcast(self.event_broadcast).
                       build())
        self._chat = Chat(self.event_broadcast)
        self._password = None
        self._job: None | Job = None
        self._inactive_room_auto_termination: None | DelayedTask = None
        self._id = uuid.uuid4().hex  # TODO: replace uuid with something more memorable
        self.event_manager = event_manager
        self.delay_room_termination()

    def player_set(self):
        """
               Retrieves the current set of players seated at the table.

               :return: A collection of players currently seated.
               :rtype: Collection[User]
        """
        return self._table.get_seat_manager().seats.values()

    def add_user(self, user: User):
        """
               Adds a user to the room and broadcasts the event to other users.

               :param user: The User object to add to the room.
               :return: None
        """
        self.users[user.id] = user
        user.room_count += 1
        if self._job is not None:
            self._job = Job(lambda: self.__empty_check())
            self.job_manager.add_job(self._job)
        welcome_event = {"type": "room_welcome_event", "room_id": self._id, "password": self._password}
        user.session.receive(welcome_event)
        self.user_list_updates += 1
        add_user_event = {
            "type": "room_user_event",
            "op": "add",
            "nr": self.user_list_updates,
            "nickname": user.username,
            "fields": {
                "username": user.username,
                "role": self.get_role_of(user)
            }
        }
        self.event_broadcast(add_user_event)
        self.delay_room_termination()

    def __empty_check(self):
        """
            Checks if the room is empty and terminates it if so.

            :return: None
        """
        if len(self.users) == 0:
            self.kill()
            self.__mark_self_for_deletion(self._id)

    def delete_user(self, user: User):
        """
               Removes a user from the room and broadcasts the event to other users.

               :param user: The User object to remove from the room.
               :return: None
        """
        if user.id in self.player_set():
            self.get_table_api().leave_table(user)

        if user.id in self.users.keys():
            user.room_count -= 1
            self.users.pop(user.id)
            self.user_list_updates += 1
            del_user_event = {
                "type": "room_user_event",
                "op": "delete",
                "nr": self.user_list_updates,
                "nickname": user.username
            }
            self.event_broadcast(del_user_event)

    def get_password(self):
        """
             Retrieves the password associated with the room, if any.

             :return: The room's password.
             :rtype: str
        """
        return self._password

    def get_id(self):
        """
               Retrieves the unique identifier of the room.

               :return: The room's unique identifier.
               :rtype: str
        """
        return self._id

    def get_table_api(self):
        """
               Retrieves the API for interacting with the room's table.

               :return: The TableApi object for the room's table.
               :rtype: TableApi
        """
        self.delay_room_termination()
        return TableApi(self._table)

    def get_role_of(self, user: User) -> str:
        """
               Determines the role of a user within the room (e.g., blue_player, red_player, spectator).

               :param user: The User object whose role is being determined.
               :return: The role of the user.
               :rtype: str
        """
        seats = self._table.get_seat_manager().seats
        for color in Side:
            if seats[color] == user.id:
                return "blue_player" if color.value else "red_player"
        return "spectator"

    def __spectator_channel(self, event_body: dict):
        """
           Sends an event to all spectators in the room.

           :param event_body: The body of the event to be sent.
           :return: None
        """
        player_set = self.player_set()
        users = [user for user in self.users.values() if user.id not in player_set]
        self.send_event_to_range(event_body, users)
    
    def send_event_to_range(self, event: dict, users: collections.Collection[User]):
        """
          Sends an event to a specified range of users.

          :param event: The event data to be sent.
          :param users: The collection of users to receive the event.
          :return: None
        """
        event["room_id"] = self._id
        sessions = [user.session for user in users]
        multi_cast_endpoint = EventLogicalEndpointWithSignature.merge(sessions, self.event_manager)
        multi_cast_endpoint.receive(event)

    def event_broadcast(self, event: dict):
        """
                Broadcasts an event to all users in the room.

                :param event: The event data to broadcast.
                :return: None
        """
        self.send_event_to_range(event, self.users.values())

    def __players_channel(self, event_body: dict, side: Side):
        """
               Sends an event to the player on the specified side (blue or red).

               :param event_body: The body of the event to be sent.
               :param side: The side (blue or red) to which the event should be sent.
               :return: None
        """
        player_id = self._table.get_seat_manager().seats.get(side, None)
        player = self.users.get(player_id)
        if player is not None:
            self.send_event_to_range(event_body, [player])

    def get_chat(self):
        """
              Retrieves the chat system associated with the room.

              :return: The Chat object for the room.
              :rtype: Chat
        """
        self.delay_room_termination()
        return self._chat

    def __on_seat_change(self, player_id, side: Side | None):
        """
              Handles seat change events and broadcasts the updated role to other users.

              :param player_id: The ID of the player whose seat has changed.
              :param side: The new side (red, blue, or None) assigned to the player.
              :return: None
        """
        new_role = "spectator"
        if side is Side.red:
            new_role = "red_player"
        elif side is Side.blue:
            new_role = "blue_player"

        user = self.users[player_id]
        self.user_list_updates += 1
        role_changed_event = {
            "type": "room_user_event",
            "op": "modify",
            "nr": self.user_list_updates,
            "nickname": user.username,
            "fields": {
                "role": new_role
            }
        }
        self.event_broadcast(role_changed_event)

    def get_table(self):
        """
               Retrieves the table associated with the room.

               :return: The Table object for the room.
               :rtype: Table
        """
        self.delay_room_termination()
        return self._table

    def kill(self):
        """
            Terminates the room and cancels any ongoing jobs or tasks.

            :return: None
        """
        self._table.kill()
        if self._job is not None:
            self._job.cancel()

        if self._inactive_room_auto_termination is not None:
            self._inactive_room_auto_termination.cancel()

    def delay_room_termination(self):
        """
             Delays the automatic termination of the room by resetting the termination task.

             :return: None
        """
        if self._inactive_room_auto_termination is not None:
            self._inactive_room_auto_termination.cancel()
        self._inactive_room_auto_termination = DelayedTask(self.close_room, 1000 * 600)
        self.job_manager.add_delayed_task(self._inactive_room_auto_termination)

    def close_room(self):
        """
           Closes the room, broadcasting the closure event and marking the room for deletion.

           :return: None
        """
        event = {
            "type": "room_closed"
        }
        self.event_broadcast(event)
        self.__mark_self_for_deletion(self._id)


class RoomApi:
    """
    RoomApi class provides a set of methods to interact with a specific room in a game. Each method is represented as
    a callback function that takes the user object and request dictionary as parameters and returns a tuple
    containing a boolean flag indicating success or failure, and an optional string or dictionary as the response
    data. The available commands are defined in the `strategies` dictionary, which maps each command type to its
    corresponding callback function.

    :param Room room: The specific room object that this API will interact with.
    :return: A tuple containing a boolean flag indicating success or failure, and an optional string or dictionary as the response data.
    """
    def __init__(self, room: Room):
        self.room = room
        self.strategies: dict[str, Callable[[User, dict], tuple[bool, str | None] | dict]] = {
            "exit_room": lambda user, req: self.exit_room(user),
            "join_room": lambda user, req: self.join(user, req),
            "get_room_users": lambda user, req: self.get_room_users(user),
            "get_board": lambda user, req: self.get_board(user),
            "get_room_info": lambda user, req: self.get_room_metadata(),
            "claim_seat": lambda user, req: self.claim_seat(user, req),
            "release_seat": lambda user, req: self.release_seat(user),
            "set_ready": lambda user, req: self.set_readiness(user, req),
            "get_ready": lambda user, req: self.get_readiness(user),
            "get_chat_metadata": lambda user, req: self.get_chat_metadata(user),
            "get_chat_messages": lambda user, req: self.get_chat_messages(user, req),
            "send_chat_message": lambda user, req: self.post_message(user, req),
            "send_setup": lambda user, req: self.send_setup(user, req),
            "send_move": lambda user, req: self.make_move(user, req),
            "leave_room": lambda user, req: self.exit_room(user),
            "set_rematch_willingness": lambda user, req: self.set_rematch_willingness(user, req)
        }

    def join(self, user: User, request: dict) -> tuple[bool, str | None]:
        if user.id in self.room.users:
            return False, "You are already in this room"
        room_password = self.room.get_password()
        if room_password is not None:
            pass_accepted = room_password == request.get("password", None)
        else:
            pass_accepted = True

        if not pass_accepted:
            return False, "wrong password"

        self.room.add_user(user)
        return True, None

    def exit_room(self, user: User) -> tuple[bool, str | None]:
        self.room.delete_user(user)
        return True, None

    def post_message(self, user: User, request: dict) -> tuple[bool, str | None]:
        if user.id not in self.room.users:
            return False, "You must join room to chat."

        chat_api = ChatApi(self.room.get_chat())
        result = chat_api.post_message(user, request)
        return result

    def get_room_users(self, user: User) -> tuple[bool, str | None] | dict:
        if user.id not in self.room.users:
            return False, "You must join room to do that."

        response = {"status": "success",
                    "nr": self.room.user_list_updates,
                    "user_list": [{"username": u.username, "role": self.room.get_role_of(u)}
                                  for u in self.room.users.values()]}

        return response

    def get_board(self, user: User) -> dict | tuple[bool, str | None]:
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().get_board(user)

    def claim_seat(self, user: User, request: dict) -> tuple[bool, str | None]:
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().take_seat(request, user)

    def release_seat(self, user: User) -> tuple[bool, str | None]:
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().release_seat(user)

    def set_readiness(self, user: User, request: dict):
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().set_readiness(request, user)

    def get_readiness(self, user: User):
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().get_player_readiness(user)

    def get_chat_metadata(self, user: User) -> tuple[bool, str | None] | dict:
        if user.id not in self.room.users.keys():
            return False, "You must join room to access chat"
        return ChatApi(self.room.get_chat()).get_chat_meta()

    def get_chat_messages(self, user: User, request: dict):
        if user.id not in self.room.users.keys():
            return False, "You must join room to access chat"
        return ChatApi(self.room.get_chat()).get_chat_messages(request)

    def send_setup(self, user: User, request: dict):
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().submit_setup(request, user)

    def make_move(self, user: User, request: dict):
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().make_move(request, user)

    def resign(self, user: User):
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().resign(user)

    def set_rematch_willingness(self, user: User, request: dict) -> tuple[bool, str | None]:
        if user.id not in self.room.users.keys():
            return False, "You must join room to access this command"
        return self.room.get_table_api().set_rematch_willingness(user, request)

    def get_room_metadata(self) -> dict:
        phases_to_string = {
            TableGamePhase.setup: "setup",
            TableGamePhase.awaiting: "awaiting",
            TableGamePhase.finished: "finished",
            TableGamePhase.gameplay: "gameplay"
        }
        response = {
            "room_id": self.room.get_id(),
            "status": "success",
            "metadata": {
                "password_required": self.room.get_password() is not None,
                "user_count": len(self.room.users),
                "game_phase": phases_to_string.get(self.room.get_table().phase_type, None)
            }
        }
        return response

    def __call__(self, user: User, request: dict) -> tuple[bool, str | None] | dict:
        """
        :param User user: The user object that is requesting an action. :param dict request: The dictionary
        containing the specific command and parameters. :return: A tuple containing a boolean flag indicating success
        or failure, and an optional string or dictionary as the response data.
        """
        request_type: str | None = request.get("type", None)
        if type(request_type) is not str:
            return False, f'Field "type" should have type str, found {type(request_type)}'
        strategy = self.strategies.get(request_type, None)
        if strategy is None:
            return False, f"Can not found room command associated with type {request_type}"
        return strategy(user, request)
