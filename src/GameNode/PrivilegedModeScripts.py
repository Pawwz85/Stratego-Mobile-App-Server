from src.Core.User import UserDto
from src.GameNode.GameManager import GameManager


class PrivilegedGameManagerSpecialRoomCreator:

    def __init__(self, game_manager: GameManager,
                 actor1: UserDto,
                 actor2: UserDto,
                 create_room_request: dict
                 ):
        self._game_manager = game_manager
        self._actor1: UserDto = actor1
        self._actor2: UserDto = actor2
        res = self._game_manager.api.create_room(self._actor1, create_room_request)
        join_room_command = None
        self._game_manager.api.resolve_command(self._actor2, join_room_command)
        