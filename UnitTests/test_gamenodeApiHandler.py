import json
import time
import unittest
from abc import abstractmethod
from unittest.mock import Mock

import redis.asyncio

from Environment.PredefinedEnvironments import (testing_environment)
from src.AsyncioWorkerThread import AsyncioWorkerThread
from src.Core.User import UserDto
from src.Frontend.IntermediateRequestIDMapper import IntermediateRequestIDMapper
from src.Frontend.message_processing import UserResponseBufferer
from src.GameNode.GameNodeConfigBuilder import GameNodeConfigBuilder
from src.InterClusterCommunication.HandleGameNodeMessage import GameNodeAPIHandler
from src.InterClusterCommunication.IEventChannelManager import IPubSub
from src.InterClusterCommunication.RedisChannelManager import RedisChannelManager


# noinspection PyMethodParameters
class TestGameNodeApiHandler(unittest.IsolatedAsyncioTestCase):

    @abstractmethod
    def setUpClass(**kwargs):
        testing_environment.setUp()
        game_node_config = (GameNodeConfigBuilder()
                            .unique_game_node_channel("node")
                            .frontend_node_cluster_broadcast_chanel("user")
                            .build())
        testing_environment.create_game_node(game_node_config)

    @abstractmethod
    def tearDownClass(**kwargs):
        testing_environment.cleanUp()

    @staticmethod
    async def setup_pub_sub(pub_sub: IPubSub, callback):
        await pub_sub.subscribe("user", callback)
        await pub_sub.listen()

    def setUp(self):
        print(testing_environment.get_broker_service_url())

        self._redis = redis.asyncio.from_url(testing_environment.get_broker_service_url())
        self._mapper = IntermediateRequestIDMapper()
        self._response_buffer = UserResponseBufferer()
        self._channel_manager = RedisChannelManager(self._redis)
        self._worker = AsyncioWorkerThread()
        self._event_broadcast = Mock()

        self._GameNodeHandler = GameNodeAPIHandler(self._mapper, self._response_buffer, self._channel_manager,
                                                   self._worker, self._event_broadcast)

        coro = self.setup_pub_sub(self._channel_manager.get_pub_sub(), self._GameNodeHandler.handle_game_node_message)
        self._worker.add_task(coro)
        self._worker.start()

    def tearDown(self):
        self._worker.stop()
        self._worker.join(10)

        del self._GameNodeHandler
        del self._redis
        del self._mapper
        del self._response_buffer
        del self._channel_manager
        del self._worker
        del self._event_broadcast

    def test_send_request_for_empty_request(self):
        req = {}
        user = UserDto("tester", "pass", 1)
        callback = Mock()
        self._GameNodeHandler.send_request(callback, req, user)
        time.sleep(9)

        args, _ = callback.call_args
        self.assertEqual("invalid_message", args[1]["type"])

    def test_send_valid_request(self):
        req = {
            "type": "browse_rooms",
            "message_id": "test",
            "channel": "node"
        }
        user = UserDto("tester", "pass", 1)
        callback = Mock()
        self._GameNodeHandler.send_request(callback, req, user)
        time.sleep(9)

        args, _ = callback.call_args
        self.assertEqual("success", args[1]["status"])

    def test_send_request_create_a_placeholder_response_in_buffer(self):
        req = {
            "type": "browse_rooms",
            "message_id": "test",
            "channel": "node"
        }
        user = UserDto("tester", "pass", 1)
        self._GameNodeHandler.send_request(lambda _, __: None, req, user)
        res = self._response_buffer.get_response("tester", "test")

        status = json.loads(res)["status"]
        self.assertEqual(status, "processing")

    def test_send_request_saves_result_to_a_response_buffer(self):
        req = {
            "type": "browse_rooms",
            "message_id": "test",
            "channel": "node"
        }
        user = UserDto("tester", "pass", 1)
        self._GameNodeHandler.send_request(lambda _, __: None, req, user)
        time.sleep(9)
        res = self._response_buffer.get_response("tester", "test")
        status = json.loads(res)["status"]
        self.assertEqual(status, "success")

    def test_on_user_request_responds_with_cached_response(self):
        req = {
            "type": "browse_rooms",
            "message_id": "test",
            "channel": "node"
        }
        user = UserDto("tester", "pass", 1)
        self._GameNodeHandler.send_request(lambda _, __: None, req.copy(), user)
        time.sleep(7)
        mock = Mock()
        self._GameNodeHandler.on_user_request_dict(user, req.copy(), mock)
        args, kwargs = mock.call_args
        self.assertEqual(args[1]["status"], "success")
