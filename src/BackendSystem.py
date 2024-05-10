"""
    This file defines a backend system, which is a main class of a worker thread.
    It controls lifecycle of other components, listens to redis pubs

    TODO: Make that every user session is a set of IEventReceivers that are associated with valid frontend channel
    TODO: Add a commend to documentation that allows player to get room time control

"""
from __future__ import annotations
import json
import math
from typing import Callable

import redis.asyncio as redis

from ResourceManager import ResourceManager
from Events import Eventmanager, IEventReceiver
from Room import Room, RoomApi
from src.User import User, UserDto
from src.table import Table
from collections import deque


class BackendSystem:

    def __init__(self):
        self.resource_manager = ResourceManager()
        self.event_manager = Eventmanager(self.resource_manager)
        self.rooms: dict[str, Room] = dict()
        self.users_connected: dict[int, User] = dict()
        with open("../Config/secret_config.properties") as file:
            self.config = json.load(file)
        self.redis = redis.from_url(self.config["redis_url"])
        self.pub_sub = self.redis.pubsub()
        self.pub_sub.subscribe(self.config["backend_api_channel_name"])

    def register_user(self, user: UserDto):
        # Todo: pass some object that would allow to push events to the user
        user_obj = User(user.username, user.password, user.user_id, self.event_manager)

        user_obj.session.endpoints.add()
        self.users_connected[user.user_id] = user_obj

    def get_room_builder(self):
        return Room.Builder(self.resource_manager, lambda _id: self.rooms.pop(_id))

    def __scans_for_pubs(self):
        new_messages: deque[str] = deque()
        while True:
            message = self.pub_sub.get_message(ignore_subscribe_messages=True)
            if message is None:
                break
            elif message["type"] == "message":
                new_messages.append(message["data"])
        return new_messages

    def __check_queue(self):
        return self.redis.rpop(self.config["request_queue_name"])

    def __check_requests(self):
        requests = self.__scans_for_pubs()
        queued = self.__check_queue()
        if queued is not None:
            requests.append(queued)
        return requests

    @staticmethod
    def parse_request(message: str) -> tuple[UserDto, dict]:
        js = json.loads(message)
        user_json: dict = js["user"]
        user_dto = UserDto(user_json["username"], user_json["password"], user_json["user_id"])
        request: dict = js["request"]
        return user_dto, request


class BackendApi:

    def __init__(self, backend_system: BackendSystem):
        self.system = backend_system

    def create_room(self, user: User, request: dict):
        time_control: int | float | None = request.get("time_control", None)
        increment: int | float | None = request.get("time_added", None)
        time_setup: int | float | None = request.get("setup_time", None)

        for field in [time_control, increment, time_setup]:
            if type(field) not in [int, float]:
                return False, f"Expected time to be type of float or int, found {type(field)}"

        ver_result = BackendApi.__verify_time_control(time_control, increment, time_setup)
        if not ver_result[0]:
            return ver_result

        table_factory = (Table.Builder(self.system.resource_manager)
                         .set_setup_time(math.ceil(60 * 1000 * time_setup))
                         .set_time_control(math.ceil(60 * 1000 * time_control), math.ceil(1000 * increment))
                         )

        password = request.get("password", None)
        password = None if password is None else str(password)

        room = (self.system.get_room_builder()
                .set_table_builder(table_factory)
                .set_password(password)
                .set_event_manager(self.system.event_manager)
                ).build()
        room.add_user(user)
        self.system.rooms[room.get_id()] = room
        return {
            "status": "success",
            "room_id": room.get_id()
        }

    def forward_request_to_room_api(self, user: User, request: dict):
        room_id: str | None = request.get("room_id", None)
        if room_id is None:
            return False, 'Request missed the necessary field "room_id"'
        room = self.system.rooms[room_id]
        return RoomApi(room)(user, request)

    @staticmethod
    def __verify_time_control(time_control: float | int, increment_time: float,
                              setup_time: float | int) -> tuple[bool, str | None]:
        with open("../Config/TimeControlsAllowed.properties") as file:
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

    def resolve_command(self, user: User, request: dict):
        request_type: str | None = request.get("type", None)
        if type(request_type) is not str:
            return False, f'Field "type" should have type str, found {type(request_type)}'

        if request_type == "create_room":
            self.create_room(user, request)

        if request.get("room_id", None) is not None:
            return self.forward_request_to_room_api(user, request)

        return False, "Could not resolve the command (missing room_id?)"

    @staticmethod
    def __produce_api_response(api_response: tuple[bool, str | None] | dict) -> dict:
        if type(api_response) is dict:
            return api_response

        success, excuse = api_response
        response = {
            "status": "success" if success else "failure"
        }
        if excuse is not None:
            response["cause"] = excuse
        return response

    def __call__(self, user: User, request: dict):
        return BackendApi.__produce_api_response(
            self.resolve_command(user, request)
        )
