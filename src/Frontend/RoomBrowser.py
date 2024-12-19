import asyncio
import uuid
from collections import deque
from collections.abc import Iterable, Callable
from dataclasses import dataclass
from threading import Lock

from src.Core.User import UserIdentity
from src.InterClusterCommunication.HandleGameNodeMessage import GameNodeAPIHandler
from src.InterClusterCommunication.IEventChannelManager import IChannelManager


@dataclass
class RoomInfo:
    id: str
    game_phase: str
    user_count: int
    password_required: bool


class GameNodeRoomListCache:
    """
        Class responsible for caching a room list from single game Node
    """
    def __init__(self, game_node_channel: str, api_handler: GameNodeAPIHandler):
        self._room_list: list[RoomInfo] = []
        self._game_node = game_node_channel
        self._game_node_api_handler = api_handler
        self._lock: Lock = Lock()
        self.sync()

    def __update_room_list(self, _: str, request: dict):
        if request["status"] != "success":
            return
        with self._lock:
            self._room_list.clear()

            for room in request["rooms"]:
                room_id = room["room_id"]
                metadata = room["metadata"]
                room_meta = RoomInfo(room_id,
                                     metadata["game_phase"],
                                     metadata["user_count"],
                                     metadata["password_required"]
                                     )
                self._room_list.append(room_meta)

    def copy_room_list(self):
        with self._lock:
            return self._room_list.copy()

    def sync(self):
        request = {
            "message_id": uuid.uuid4().hex,
            "channel": self._game_node,
            "type": "browse_rooms"
        }
        print(request)
        empty_user = UserIdentity("SYSTEM", -1)

        self._game_node_api_handler.on_user_request_dict(empty_user, request, callback=self.__update_room_list)


class GlobalRoomListCache:

    def __init__(self, api_handler: GameNodeAPIHandler, channel_manager: IChannelManager):
        self._channel_manager = channel_manager
        self._game_node_api_handler = api_handler
        self._game_nodes: dict[str, GameNodeRoomListCache] = dict()
        self._rooms_meta: deque[RoomInfo] = deque()
        self._lock = Lock()

    def _update_node_list(self, channels: list[str]):
        channels = {x for x in channels}

        for n in channels - self._game_nodes.keys():
            self._game_nodes[n] = GameNodeRoomListCache(n, self._game_node_api_handler)

        for n in self._game_nodes.keys() - channels:
            self._game_nodes.pop(n)

    def copy_room_meta(self):
        result = []
        with self._lock:
            result.extend(self._rooms_meta)
        return result

    async def sync(self, sync_rate: float = 10.):
        while True:
            self._rooms_meta.clear()

            for n in self._game_nodes.values():
                self._rooms_meta.extend(n.copy_room_list())

            channels = await self._channel_manager.get_group_manager().get_group("game_nodes")
            self._update_node_list(channels)

            for cache in self._game_nodes.values():
                cache.sync()

            await asyncio.sleep(sync_rate)


class RoomBrowser:

    def __init__(self, cache: GlobalRoomListCache):
        self._cache = cache

    def browse(self, filter_by: Callable[[RoomInfo], bool] = lambda x: True,
               sort_by=None, reverse=False) -> Iterable[RoomInfo]:
        rooms_info = self._cache.copy_room_meta()
        if sort_by is not None:
            rooms_info.sort(key=sort_by, reverse=reverse)
        filtered = filter(filter_by, rooms_info)
        return filtered
