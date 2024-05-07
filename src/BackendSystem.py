"""
    This file defines a backend system, which is a main class of a worker thread.
    It controls lifecycle of other components, listens to redis pubs

    TODO: Go back to drawing board, think some more time about vision and define user DTO (JSON?)
    TODO: Create a forwarding mechanism between BackendApi and a room api
    TODO: Add a commend to documentation that allows player to get room time control

"""
import json
import math

import redis.asyncio as redis
from ResourceManager import ResourceManager
from Events import Eventmanager
from Room import Room, RoomApi
from src.User import User, UserDto
from src.table import Table


class BackendSystem:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.event_manager = Eventmanager(self.resource_manager)
        self.rooms: dict[str, Room] = dict()
        self.users_connected: dict[int, User] = dict()

    def register_user(self, user: UserDto):
        # Todo: pass some object that would allow to push events to the user
        user_obj = User(user.username, user.password, user.user_id, self.event_manager)
        self.users_connected[user.user_id] = user_obj

    def get_room_builder(self):
        return Room.Builder(self.resource_manager, lambda _id: self.rooms.pop(_id))


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
                ).build()
        room.add_user(user)
        self.system.rooms[room.get_id()] = room
        return {
            "status": "success",
            "room_id": room.get_id()
        }

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
