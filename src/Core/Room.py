from __future__ import annotations
from typing import Callable
import uuid

from src.Core.ResourceManager import ResourceManager, ResourceManagerJob
from src.Core.User import User
from src.Core.stratego import Side
from src.Core.table import Table, TableApi
from src.Core.chat import Chat, ChatApi
from src.Events.Events import EventLogicalEndpointWithSignature, Eventmanager


class Room:
    class Builder:
        def __init__(self, resource_manager: ResourceManager, mark_for_deletion: Callable[[str], any]):
            self.resourceManager = resource_manager
            self.event_manager: Eventmanager = Eventmanager(resource_manager)
            self.table_builder = Table.Builder(resource_manager)
            self.chat_cap = 1024
            self.password: str | None = None
            self.mark_for_deletion: Callable = mark_for_deletion

        def set_table_builder(self, table_builder: Table.Builder):
            self.table_builder = table_builder
            return self

        def set_chat_cap(self, size: int):
            self.chat_cap = size
            return self

        def set_password(self, password: str | None):
            self.password = password
            return self

        def set_event_manager(self, event_manager: Eventmanager):
            self.event_manager = event_manager
            return self

        def build(self) -> Room:
            result: Room = Room(self.resourceManager, self.event_manager, self.table_builder, self.mark_for_deletion)
            result._chat = Chat(result.event_broadcast, self.chat_cap)
            result._password = self.password
            return result

    def __init__(self, resource_manager: ResourceManager, event_manager: Eventmanager,
                 table_builder: Table.Builder, mark_for_deletion: Callable[[str], any]):
        self.users: dict[int, User] = dict()
        self.user_list_updates = 0
        self.resourceManager = resource_manager
        self.__mark_self_for_deletion = mark_for_deletion
        self._table = (table_builder.
                       set_seat_observer(self.__on_seat_change).
                       set_event_channels({None: self.__spectator_channel,
                                           Side.blue: lambda body: self.__players_channel(body, Side.blue),
                                           Side.red: lambda body: self.__players_channel(body, Side.red)}).
                       build())
        self._chat = Chat(self.event_broadcast)
        self._password = None
        self._job: None | ResourceManagerJob = None
        self._id = uuid.uuid4().hex  # TODO: replace uuid with something more memorable
        self.event_manager = event_manager

    def player_set(self):
        return self._table.get_seat_manager().seats.values()

    def add_user(self, user: User):
        self.users[user.id] = user
        user.room_count += 1
        if self._job is not None:
            self._job = ResourceManagerJob(lambda: self.__empty_check())
            self.resourceManager.add_job(self._job)
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

    def __empty_check(self):
        if len(self.users) == 0:
            self.kill()
            self.__mark_self_for_deletion(self._id)

    def delete_user(self, user: User):
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
        return self._password

    def get_id(self):
        return self._id

    def get_table_api(self):
        return TableApi(self._table)

    def get_role_of(self, user: User) -> str:
        seats = self._table.get_seat_manager().seats
        for color in Side:
            if seats[color] == user.id:
                return "blue_player" if color.value() else "red_player"
        return "spectator"

    def __spectator_channel(self, event_body: dict):
        player_set = self.player_set()
        event_body["room_id"] = self._id

        sessions = [user.session for user in self.users.values() if user.id not in player_set]
        multi_cast_endpoint = EventLogicalEndpointWithSignature.merge(sessions, self.event_manager)
        multi_cast_endpoint.receive(event_body)

    def event_broadcast(self, event: dict):
        event["room_id"] = self._id
        sessions = [user.session for user in self.users.values()]
        multi_cast_endpoint = EventLogicalEndpointWithSignature.merge(sessions, self.event_manager)
        multi_cast_endpoint.receive(event)

    def __players_channel(self, event_body: dict, side: Side):
        # We can send this directly to users, as mplayer numbers is always small (1 or 0)
        player_id = self._table.get_seat_manager().seats.get(side, None)
        player = self.users.get(player_id)
        event_body["room_id"] = self._id
        if player is not None:
            player.session.receive(event_body)

    def get_chat(self):
        return self._chat

    def __on_seat_change(self, player_id, side: Side | None):
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
        return self._table

    def kill(self):
        self._table.kill()
        if self._job is not None:
            self._job.cancel()


class RoomApi:
    def __init__(self, room: Room):
        self.room = room
        self.strategies: dict[str, Callable[[User, dict], tuple[bool, str | None] | dict]] = {
            "exit_room": lambda user, req: self.exit_room(user),
            "get_room_users": lambda user, req: self.get_room_users(user),
            "get_board": lambda user, req: self.get_board(user),
            "claim_seat": lambda user, req: self.claim_seat(user, req),
            "release_seat": lambda user, req: self.release_seat(user),
            "set_ready": lambda user, req: self.set_readiness(user, req),
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

    def __call__(self, user: User, request: dict) -> tuple[bool, str | None] | dict:
        request_type: str | None = request.get("type", None)
        if type(request_type) is not str:
            return False, f'Field "type" should have type str, found {type(request_type)}'
        strategy = self.strategies.get(request_type, None)
        if strategy is None:
            return False, f"Can not found room command associated with type {request_type}"
        return strategy(user, request)
