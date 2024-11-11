"""
    This file defines a backend system, which is a main class of a worker thread.
    It controls lifecycle of other components, listens to redis pubs

"""
from __future__ import annotations

import asyncio
import multiprocessing
import signal
import threading
from threading import Lock

from src.Core.Room import IRoomHandle
from src.GameNode.GameManagerThread import GameManagerThread
from src.InterClusterCommunication.IEventChannelManager import IChannelManager


class PubSubSyncHandle(IRoomHandle):

    def __init__(self, channel_man: IChannelManager, channel_name: str):
        self._lock = Lock()
        self._channel = channel_name
        self._channel_man = channel_man
        self._key: str | None = None
        self._key_claim_request = threading.Event()
        self._key_claimed = threading.Event()
        self._released = threading.Event()

    def claim(self, room_id: str):
        with self._lock:
            self._key = room_id
            self._key_claim_request.set()

    def release(self):
        with self._lock:
            self._released.set()

    async def health_check(self):
        await self._await_key()
        await self._await_release()

    async def _await_key(self):
        while True:
            if self._key_claim_request.is_set():
                print(f"setting route from {self._key} to {self._channel}")
                await self._channel_man.get_routing_manager().set_routing(self._key, self._channel)
                break
            else:
                await asyncio.sleep(0.01)  # Busy wait to

    async def _await_release(self):
        while True:
            if self._released.is_set():
                print(f"discarding route for {self._key}")
                await self._channel_man.get_routing_manager().discard_routing(self._key)
                break
            else:
                await asyncio.sleep(600)


class GameNode:

    def __init__(self, config: dict, channel_manager: IChannelManager):
        self._config = config
        self._loop = asyncio.new_event_loop()
        self._channel_manager = channel_manager
        self._channel_manager_lock = Lock()
        self._private_channel_name = self._config["unique_game_node_channel"]

        self._game_thread = GameManagerThread(self.create_room_handle)
        self._shutdown_flag = multiprocessing.Event()
        self._msg_broker_handle: str | None = None
        signal.signal(signal.SIGINT, lambda _, __: self.shutdown())
        signal.signal(signal.SIGTERM, lambda _, __: self.shutdown())

    def create_room_handle(self):
        print("Creating handle")
        result = PubSubSyncHandle(self._channel_manager, self._private_channel_name)
        asyncio.run_coroutine_threadsafe(result.health_check(), self._loop)
        return result

    def __resolve_call(self, request: str):
        print(request)
        self._game_thread.write_request(request)

    async def _register_game_node(self):
        self._msg_broker_handle = await self._channel_manager.get_group_manager().add_channel_to_group(
            self._private_channel_name, "game_nodes"
        )

    def _unregister_game_node(self):
        if self._msg_broker_handle:
            group_man = self._channel_manager.get_group_manager()
            coro = group_man.remove_channel_from_group(self._msg_broker_handle)
            self._loop.run_until_complete(coro)

    def run(self):
        self._game_thread.start()
        self._loop.run_until_complete(self._register_game_node())
        self._loop.create_task(self.__sub_and_listen())
        self._loop.create_task(self._channel_manager.get_request_queue_worker().consume_requests(self.__resolve_call))
        self._loop.create_task(self.__attempt_shutdown())
        self._loop.create_task(self.__send_responses_and_requests())

        self._loop.run_forever()
        self._game_thread.join()
        self._unregister_game_node()

    async def __sub_and_listen(self):
        pub_sub = self._channel_manager.get_pub_sub()
        await pub_sub.subscribe(self._private_channel_name, self.__resolve_call)
        await pub_sub.listen()

    async def __attempt_shutdown(self):
        while True:
            if self._shutdown_flag.is_set():
                self._game_thread.stop()
                self._loop.stop()
            await asyncio.sleep(10)

    def shutdown(self):
        self._shutdown_flag.set()

    async def __send_responses_and_requests(self):
        pub_sub = self._channel_manager.get_pub_sub()
        while True:
            msgs = self._game_thread.retrieve_responses_and_events()
            for msg in msgs:
                print(msg)
                await pub_sub.publish(self._config["frontend_node_cluster_broadcast_chanel"], msg)

            await asyncio.sleep(0.01)
