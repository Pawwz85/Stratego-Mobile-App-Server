import time

import redis

from Environment.IEnvironment import IEnvironment
from multiprocessing import Process

from src.GameNode.GameNode import GameNode
from src.InterClusterCommunication.RedisChannelManager import RedisChannelManager


def run_game_node(config: dict):
    redis_ = redis.asyncio.from_url(config["redis_url"])
    channel_manager = RedisChannelManager(redis_)
    node = GameNode(config, channel_manager)
    node.run()


class RedisEnvironment(IEnvironment):
    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis = redis.from_url(redis_url)
        self._game_nodes: dict[int, Process] = dict()
        self._id_schema = 0

    def _generate_id(self):
        result = self._id_schema
        self._id_schema = self._id_schema + 1
        return result

    def setUp(self):
        pass

    def cleanUp(self):
        self._redis.flushall()
        game_nodes_handles = [key for key in self._game_nodes.keys()]
        for handle in game_nodes_handles:
            self.destroy_game_node(handle)

    def create_game_node(self, config: dict) -> int:
        config_copy = config.copy()
        config_copy["redis_url"] = self._redis_url
        node_process = Process(target=run_game_node, args=(config_copy,))
        identifier = self._generate_id()
        self._game_nodes[identifier] = node_process
        node_process.start()
        return identifier

    def destroy_game_node(self, node_handle: int):

        try:
            proc = self._game_nodes[node_handle]
            proc.kill()
            proc.join(15.)
            self._game_nodes.pop(node_handle)
        except KeyError:
            print('Invalid handle')

    def get_broker_service_url(self) -> str:
        return self._redis_url