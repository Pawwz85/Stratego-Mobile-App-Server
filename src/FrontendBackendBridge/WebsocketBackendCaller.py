import json
from redis import Redis
from flask_socketio import SocketIO

from src.Core.User import UserDto
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategy, BackendResponseStrategyRepository
from src.FrontendBackendBridge.IBackendCaller import IBackendCaller
from src.message_processing import ResponseBufferer


class WebsocketBackendCaller(IBackendCaller):
    def __init__(self, strategy_repository: BackendResponseStrategyRepository,
                 redis: Redis, config: dict,
                 socketIO: SocketIO,
                 response_bufferer: ResponseBufferer):
        self.socketIO = socketIO
        self.response_bufferer = response_bufferer
        super().__init__(strategy_repository, redis, config)

    def handle_response(self, response: dict, room_name: str):
        response_id = response["message_id"]
        self.response_bufferer.add_response(response_id, json.dumps(response))
        self.socketIO.send(response, json=True, to=room_name)

    def create_response_handling_strategy(self, command: dict, user: UserDto) -> BackendResponseStrategy:
        result: BackendResponseStrategy | None = None

        try:
            request_id = command["message_id"]
            room_name = "user_" + str(user.user_id)
            result = BackendResponseStrategy(request_id, lambda d: self.handle_response(d, room_name))
        except KeyError as e:
            result = None

        return result if result is not None else BackendResponseStrategy("", lambda x: None)
