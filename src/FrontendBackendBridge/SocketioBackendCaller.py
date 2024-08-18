import json

from flask_socketio import SocketIO
from redis import Redis

from src.Core.User import UserDto
from src.Frontend.socketio_socket_management import send_event_to_user, SocketManager
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategy, BackendResponseStrategyRepository
from src.FrontendBackendBridge.IBackendCaller import IBackendCaller
from src.Frontend.message_processing import UserResponseBufferer


class SocketioBackendCaller(IBackendCaller):
    def __init__(self, strategy_repository: BackendResponseStrategyRepository,
                 redis: Redis, config: dict,
                 app: SocketIO):
        self.app = app
        super().__init__(strategy_repository, redis, config)

    def handle_response(self, response: dict, username: str):
        send_event_to_user(self.app, response, username)

    def create_response_handling_strategy(self, command: dict, user: UserDto) -> BackendResponseStrategy:
        result: BackendResponseStrategy | None = None

        try:
            request_id = command["message_id"]
            result = BackendResponseStrategy(request_id, lambda d: self.handle_response(d, user.username))
        except KeyError as e:
            result = None

        return result if result is not None else BackendResponseStrategy("", lambda x: None)
