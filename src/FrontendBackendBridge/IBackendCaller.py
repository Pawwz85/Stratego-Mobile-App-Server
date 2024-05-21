import json
import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Callable

from redis import Redis

from src.Core.User import UserDto
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategy, BackendResponseStrategyRepository

"""
    TODO: integrate this class with BackendStrategyRepository and BackendStrategyPicker
"""


class IBackendCaller(ABC):

    def __init__(self, strategy_repository: BackendResponseStrategyRepository, redis: Redis, config: dict):
        self.__strategy_repository = strategy_repository
        self.redis = redis
        self.config = config

    def __strategy_timeout(self, strategy: BackendResponseStrategy, delay: float, on_time_out: Callable):
        time.sleep(delay)
        self.__strategy_repository.remove_strategy(strategy)
        if strategy.get_times_applied() == 0:
            on_time_out()

    def __schedule_strategy_timeout(self, strategy: BackendResponseStrategy, delay: float, on_time_out: Callable):
        thread = threading.Thread(target=self.__strategy_timeout, args=(strategy, delay, on_time_out))
        thread.start()

    @staticmethod
    def __set_response_id(new_id: str, response: dict) -> dict:
        result = response.copy()
        result["response_id"] = new_id
        return result

    @staticmethod
    def wrap_strategy_with_mapping(original_request_id: str, generated_response_id: str,
                                   raw_strategy: BackendResponseStrategy) -> BackendResponseStrategy:
        """
        Wraps the provided raw strategy with a new strategy that maps the response to the original request ID.

        Args:
            original_request_id (str): The original request ID associated with the command message.
            generated_response_id (str): The response ID generated by the caller for the corresponding command.
            raw_strategy (BackendResponseStrategy): The raw strategy provided by the backend API service.

        Returns:
            BackendResponseStrategy: A new strategy that maps the response to the original request ID.

        Raises:
            ValueError: If any of the input parameters are not of the expected types or if the `raw_strategy` is invalid.
        """
        wrapped_strategy = BackendResponseStrategy(
            generated_response_id,
            lambda res: raw_strategy(IBackendCaller.__set_response_id(original_request_id, res))
        )
        return wrapped_strategy

    @abstractmethod
    def create_response_handling_strategy(self, command: dict, user: UserDto) -> BackendResponseStrategy:
        pass

    def call_all_nodes(self, command: dict, user: UserDto):
        message = {
            "user": user,
            "request": command
        }
        self.redis.publish(self.config["backend_api_channel_name"], json.dumps(message))

    def call_random_node(self, command: dict, user: UserDto):
        message = {
            "user": user,
            "request": command
        }
        self.redis.rpush(self.config["request_queue_name"], json.dumps(message))

    def call(self, command: dict, user: UserDto, time_out: float, on_time_out: Callable):
        command = command.copy()
        response_handling_strategy = self.create_response_handling_strategy(command, user)

        # hide a user given message_id behind uuid, so we ids would be unique amongst all the users
        original_msg_id = command.get("message_id")
        command["message_id"] = uuid.uuid4().hex
        self.__strategy_repository.add_strategy(self.wrap_strategy_with_mapping(
            original_msg_id,
            command["message_id"],
            response_handling_strategy)
        )
        self.__schedule_strategy_timeout(response_handling_strategy, time_out, on_time_out)

        if command.get("type") == "create_room":
            return self.call_random_node(command, user)
        else:
            return self.call_all_nodes(command, user)
