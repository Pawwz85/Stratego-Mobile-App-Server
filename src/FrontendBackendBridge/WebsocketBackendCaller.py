import json
from redis import Redis

from src.Core.User import UserDto
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategy, BackendResponseStrategyRepository
from src.FrontendBackendBridge.IBackendCaller import IBackendCaller
from src.message_processing import ResponseBufferer


class WebsocketBackendCaller(IBackendCaller):
    def __init__(self, strategy_repository: BackendResponseStrategyRepository,
                 redis: Redis, config: dict,
                 websocket_service,
                 response_bufferer: ResponseBufferer):
        self.web_socket_service = websocket_service
        self.response_bufferer = response_bufferer
        super().__init__(strategy_repository, redis, config)

    def handle_response(self, response: dict, username: str):
        response_id = response["response_id"]
        self.response_bufferer.add_response(response_id, json.dumps(response))
        self.web_socket_service.send_msg_to_user(response, username)

    def create_response_handling_strategy(self, command: dict, user: UserDto) -> BackendResponseStrategy:
        result: BackendResponseStrategy | None = None

        try:
            request_id = command["message_id"]
            result = BackendResponseStrategy(request_id, lambda d: self.handle_response(d, user.username))
        except KeyError as e:
            result = None

        return result if result is not None else BackendResponseStrategy("", lambda x: None)
