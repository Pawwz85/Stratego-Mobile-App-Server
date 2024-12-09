import os
import time
from pathlib import Path
from redis import Redis
from redis.asyncio import Redis as Asyncio_redis

from Environment.IEnvironment import IEnvironment
import subprocess
from multiprocessing import Process
import setproctitle

from Environment.LocalMessageBrokerServiceBoot import ILocalMessageBrokerBoot
from src.Core.singleton import singleton
from src.GameNode.GameNode import GameNode
from src.InterClusterCommunication.RedisChannelManager import RedisChannelManager


@singleton
class RedisServerBootManager(ILocalMessageBrokerBoot):
    def boot(self):
        if not self.is_booting:
            proc = subprocess.Popen([self.boot_script], stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
            print(f"Redis booted wth pid {proc.pid}")
            self.is_booting = True

    def shutdown(self):
        print("Killing process...")
        pass

    def __init__(self, boot_script: Path | str, url: str):
        print(boot_script)
        self.url = url
        self.is_booting = False
        self.boot_script = boot_script

    def is_available(self) -> bool:
        ping_failed = False
        try:
            redis_ = Redis.from_url(self.url)
            redis_.ping()
            print(f"{self.url} pinged successfully")
        except BaseException:
            ping_failed = True
        return not ping_failed


def run_game_node(config: dict, process_name: str):
    print(config)
    setproctitle.setproctitle(process_name)
    redis_ = Asyncio_redis.from_url(config["redis_url"])
    channel_manager = RedisChannelManager(redis_)
    node = GameNode(config, channel_manager)
    print('Running node')
    node.run()


class RedisEnvironment(IEnvironment):
    def __init__(self, redis_url: str, msg_broker_boot: ILocalMessageBrokerBoot | None = None):
        super().__init__(msg_broker_boot)
        self._redis_url = redis_url
        self._redis = Redis.from_url(redis_url)
        self._game_nodes: dict[int, Process] = dict()
        self._id_schema = 0

    def _generate_id(self):
        result = self._id_schema
        self._id_schema = self._id_schema + 1
        return result

    def setUp(self):
        pass

    def cleanUp(self):
        game_nodes_handles = [key for key in self._game_nodes.keys()]
        for handle in game_nodes_handles:
            self.destroy_game_node(handle)
        self._redis.flushall()

    def create_game_node(self, config: dict) -> int:
        print("creating game node with config", config)
        config_copy = config.copy()
        config_copy["redis_url"] = self._redis_url
        identifier = self._generate_id()
        process_name = f"stratego_game_node_{identifier}"
        node_process = Process(name=process_name, target=run_game_node, args=(config_copy, process_name))
        node_process.start()
        self._game_nodes[identifier] = node_process
        print(f"Node started with identifier {identifier}, {node_process}")
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
