"""
    This file defines a backend system, which is a main class of a worker thread.
    It controls lifecycle of other components, listens to redis pubs

"""
from __future__ import annotations

import json
import math
from collections import deque
from collections.abc import Callable

from src.Core.JobManager import JobManager, DelayedTask
from src.Core.Room import Room, RoomApi, IRoomHandle
from src.Core.User import User, UserDto
from src.Core.table import Table
from src.Events.Events import Eventmanager, IEventReceiver


class GameManager:

    def __init__(self, job_manager: JobManager,
                 event_receiver_factory: Callable[[Eventmanager], IEventReceiver],
                 room_handle_factory: Callable[[], IRoomHandle] = lambda: IRoomHandle()):
        self.api = GameManagerApi(self)
        self.job_manager = job_manager
        self.event_manager = Eventmanager(self.job_manager)
        self.rooms: dict[str, Room] = dict()
        self.users_connected: dict[int, User] = dict()
        self.eventReceiver = event_receiver_factory(self.event_manager)
        self.handle_factory_method = room_handle_factory

    def register_user(self, user: UserDto):
        if user.user_id not in self.users_connected.keys():
            user_obj = User(user.username, user.password, user.user_id, self.event_manager)
            user_obj.session.endpoints.add(self.eventReceiver)
            self.users_connected[user.user_id] = user_obj

    def get_room_builder(self):
        return Room.Builder(self.job_manager, lambda _id: self.rooms.pop(_id))

    def __user_garbage_collector(self):
        users_to_remove = deque()
        for id_, user in self.users_connected.items():
            if user.room_count == 0:
                users_to_remove.append(id_)
        for id_ in users_to_remove:
            self.users_connected.pop(id_)
        next_check = DelayedTask(self.__user_garbage_collector, 60 * 1000)
        self.job_manager.add_delayed_task(next_check)

    def schedule_periodic_user_garbage_collection(self):
        self.job_manager.add_delayed_task(DelayedTask(self.__user_garbage_collector, 60 * 1000))

    def close_all_rooms(self):
        for room in self.rooms.values():
            room.close_room()


class GameManagerApi:

    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager

    def browse_rooms(self, user: User, request: dict) -> dict:
        response = {
            "status": "success",
            "rooms": [RoomApi(room).get_room_metadata() for room in self.game_manager.rooms.values()]
        }

        for r in response["rooms"]:
            r.pop("status")

        return response

    def create_room(self, user: User, request: dict):
        time_control: int | float | None = request.get("time_control", None)
        increment: int | float | None = request.get("time_added", None)
        time_setup: int | float | None = request.get("setup_time", None)

        for field in [time_control, increment, time_setup]:
            if type(field) not in [int, float]:
                return False, f"Expected time to be type of float or int, found {type(field)}"

        ver_result = GameManagerApi.__verify_time_control(time_control, increment, time_setup)
        if not ver_result[0]:
            return ver_result

        table_factory = (Table.Builder(self.game_manager.job_manager)
                         .set_setup_time(math.ceil(60 * 1000 * time_setup))
                         .set_time_control(math.ceil(60 * 1000 * time_control), math.ceil(1000 * increment))
                         )
        print(request)
        password = request.get("password", None)
        password = None if password is None else str(password)

        room = (self.game_manager.get_room_builder()
                .set_table_builder(table_factory)
                .set_password(password)
                .set_event_manager(self.game_manager.event_manager)
                .set_room_handle(self.game_manager.handle_factory_method())
                ).build()
        room.add_user(user)
        self.game_manager.rooms[room.get_id()] = room
        return {
            "status": "success",
            "room_id": room.get_id()
        }

    def forward_request_to_room_api(self, user: User, request: dict):
        room_id: str | None = request.get("room_id", None)
        if room_id is None:
            return False, 'Request missed the necessary field "room_id"'
        try:
            room = self.game_manager.rooms[room_id]
        except KeyError:
            room = None
        return RoomApi(room)(user, request) if room is not None else None

    @staticmethod
    def __verify_time_control(time_control: float | int, increment_time: float,
                              setup_time: float | int) -> tuple[bool, str | None]:
        with open("Config/TimeControlsAllowed.properties") as file:
            config = json.load(file)

        proposed_time_control = {"setup_time_minutes": setup_time,
                                 "increment_seconds": increment_time,
                                 "playing_time_minutes": time_control}

        for var in proposed_time_control.keys():
            if config["min_" + var] > proposed_time_control[var]:
                return False, f'{var} value is too big'
            if config["max_" + var] < proposed_time_control[var]:
                return False, f'{var} value is too small'

        return True, None

    def resolve_command(self, user: User, request: dict) -> tuple[bool, str | None] | dict[str, any] | None:
        request_type: str | None = request.get("type", None)
        if type(request_type) is not str:
            return False, f'Field "type" should have type str, found {type(request_type)}'

        if request_type == "create_room":
            return self.create_room(user, request)

        if request_type == "browse_rooms":
            return self.browse_rooms(user, request)

        if request.get("room_id", None) is not None:
            return self.forward_request_to_room_api(user, request)

        return False, "Could not resolve the command (missing room_id?)"

    @staticmethod
    def __produce_api_response(api_response: tuple[bool, str | None] | dict | None) -> dict | None:
        if type(api_response) is dict or api_response is None:
            return api_response

        success, excuse = api_response
        response = {
            "status": "success" if success else "failure"
        }
        if excuse is not None:
            response["cause"] = excuse
        return response

    def __call__(self, user: User, request: dict):
        return GameManagerApi.__produce_api_response(
            self.resolve_command(user, request)
        )
