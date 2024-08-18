"""
    This file defines a backend system, which is a main class of a worker thread.
    It controls lifecycle of other components, listens to redis pubs

"""
from __future__ import annotations
import json
import math

import redis as redis

from src.Core.JobManager import JobManager, DelayedTask, Job
from src.Events.Events import Eventmanager
from src.Events.RedisEventReceiver import RedisPubSubEventReceiver
from src.Core.Room import Room, RoomApi
from src.Core.User import User, UserDto
from src.Core.table import Table
from collections import deque


class BackendSystem:

    def __init__(self):
        self.api = BackendApi(self)
        self.job_manager = JobManager()
        self.event_manager = Eventmanager(self.job_manager)
        self.rooms: dict[str, Room] = dict()
        self.users_connected: dict[int, User] = dict()
        with open("../Config/secret_config.properties") as file:
            self.config = json.load(file)
        self.redis = redis.from_url(self.config["redis_url"])
        self.pub_sub = self.redis.pubsub()
        self.pub_sub.subscribe(self.config["backend_api_channel_name"])
        self.eventReceiver = RedisPubSubEventReceiver(lambda: None, self.event_manager, self.redis,
                                                      self.config["frontend_api_channel_name"])

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

    def iterate_requests(self):
        reqs = self.__check_requests()
        for req in reqs:
            user_dto, request_body = BackendSystem.parse_request(req)
            self.register_user(user_dto)
            user = self.users_connected[user_dto.user_id]
            response = self.api(user, request_body)
            if response is not None:
                response["response_id"] = request_body["message_id"]
                self.redis.publish(self.config["frontend_api_channel_name"], json.dumps(response))

    def run(self):
        self.job_manager.add_delayed_task(DelayedTask(self.__user_garbage_collector, 60 * 1000))
        self.job_manager.add_job(Job(self.iterate_requests))

        while True:
            self.job_manager.iteration_of_job_execution()


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

        table_factory = (Table.Builder(self.system.job_manager)
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
        try:
            room = self.system.rooms[room_id]
        except KeyError:
            room = None
        return RoomApi(room)(user, request) if room is not None else None

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
            return self.create_room(user, request)

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
        return BackendApi.__produce_api_response(
            self.resolve_command(user, request)
        )


if __name__ == "__main__":
    sys = BackendSystem()
    sys.run()
