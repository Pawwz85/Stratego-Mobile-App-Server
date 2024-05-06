"""
    This file defines a backend system, which is a main class of a worker thread.
    It controls lifecycle of other components, listens to redis pubs

    TODO: Implement this
"""
from ResourceManager import ResourceManager
from Events import Eventmanager
from Room import Room, RoomApi
from src.User import User


class BackendSystem:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.event_manager = Eventmanager(self.resource_manager)
        self.rooms: dict[str, Room] = dict()
        self.users_connected: dict[str, User] = dict()

    def register_user(self):
        
        pass