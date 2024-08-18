import asyncio
import json

from redis import Redis

from src.Core.User import UserDto
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategy, BackendResponseStrategyRepository
from src.FrontendBackendBridge.IBackendCaller import IBackendCaller
from threading import Lock

from src.Frontend.message_processing import UserResponseBufferer


class _SharedResource:
    def __init__(self):
        self.lock = Lock()
        self.message: None | dict = None
        self.modified: bool = False


class _CrossThreadBackendCaller(IBackendCaller):
    """
        A primitive implementation of a game node caller. Since __on_receive() will be executed on thread other
        than that call() was called, we need to deal with threading locks.
    """

    def __on_receive(self, command: dict):
        with self.response.lock:
            self.response.message = command
            self.response.modified = True

    def reset(self):
        with self.response.lock:
            self.response.message = None
            self.response.modified = False

    def create_response_handling_strategy(self, command: dict, user: UserDto) -> BackendResponseStrategy:
        result: None | BackendResponseStrategy = None
        try:
            request_id = command["message_id"]
            result = BackendResponseStrategy(request_id, self.__on_receive)
        except KeyError as e:
            result = BackendResponseStrategy("", self.__on_receive)
        return result

    def timeout(self):
        with self.response.lock:
            self.response.message = None
            self.response.modified = True

    def __init__(self, strategy_repository: BackendResponseStrategyRepository, redis: Redis, config: dict):
        super().__init__(strategy_repository, redis, config)
        self.response = _SharedResource()


class AsynchronousGameNodeQuery:
    """
        Wraps up an inherently threaded BackendCaller into an asyncio function.
        Note, that this function is not an asyncio safe, so it should be connection private
    """

    def __init__(self, strategy_repository: BackendResponseStrategyRepository, redis: Redis, config: dict):
        self.__caller = _CrossThreadBackendCaller(strategy_repository, redis, config)

    async def call(self, command: dict, user: UserDto, time_out: float) -> dict | None:
        self.__caller.call(command, user, time_out, self.__caller.timeout)
        next_iter = True
        total_time_spend = 0
        result = None
        while next_iter and total_time_spend < time_out:
            await asyncio.sleep(0.001)
            total_time_spend += 0.001
            with self.__caller.response.lock:
                if self.__caller.response.modified:
                    result = self.__caller.response.message
                    next_iter = False
        self.__caller.reset()  # resets the caller object, so we can reuse it for a next call
        return result


class BufferedGameNodeCaller(IBackendCaller):
    """
        This caller uses as response bufferer thread to store responses.
        It will immediately return a value, even if response was not received yet, giving
        it a "processing status"
    """

    def __init__(self, user_response_bufferer: UserResponseBufferer,
                 strategy_repository: BackendResponseStrategyRepository, redis: Redis, config: dict):
        super().__init__(strategy_repository, redis, config)
        self.user_response_bufferer: UserResponseBufferer = user_response_bufferer

    def create_response_handling_strategy(self, command: dict, user: UserDto) -> BackendResponseStrategy:
        foo = lambda msg: (self.user_response_bufferer.add_response(
            user.username, msg["response_id"], json.dumps(msg)))
        return BackendResponseStrategy(command["message_id"], foo)


class SynchronousGameNodeQuery:
    def __init__(self, user_response_bufferer: UserResponseBufferer,
                 strategy_repository: BackendResponseStrategyRepository, redis: Redis, config: dict):
        self.__caller = BufferedGameNodeCaller(user_response_bufferer, strategy_repository, redis, config)
        self.__user_response_buffer = user_response_bufferer

    def __timeout(self, command: dict, user: UserDto):
        response = {
            "response_id": command["message_id"],
            "status": "timed out"
        }
        self.__user_response_buffer.add_response(user.username, command["message_id"], json.dumps(response))

    def call(self, command: dict, user: UserDto, time_out: float) -> dict | None:
        cached_response = self.__user_response_buffer.get_response(user.username, command["message_id"])
        if cached_response is None:
            response = {
                "response_id": command["message_id"],
                "status": "processing"
            }
            self.__user_response_buffer.add_response(user.username, command["message_id"], json.dumps(response))
            self.__caller.call(command, user, time_out, lambda: self.__timeout(command, user))
            return response
        return json.loads(cached_response)
