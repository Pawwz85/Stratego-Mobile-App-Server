import asyncio
import json
from threading import Thread, Lock

from redis import Redis
from websockets import serve, WebSocketServerProtocol

from src.Authenticathion.Authenticator import Authenticator
from src.Core.User import UserDto
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategyRepository
from src.FrontendBackendBridge.WebsocketBackendCaller import WebsocketBackendCaller
from src.message_processing import ResponseBufferer, decode_json, check_message_type, UserMessageType


class WebsocketService(Thread):
    class WebsocketSession:
        def __init__(self):
            self.user: UserDto | None = None
            self.ill_formatted_msgs_send = 0

    def __init__(self, path: str, response_bufferer: ResponseBufferer,
                 redis: Redis, config: dict,
                 backend_strategy_repository: BackendResponseStrategyRepository):
        super().__init__()
        self.lock = Lock()
        self.path = path
        self.response_bufferer = response_bufferer
        self.__user_usernames_to_websockets: dict[str, WebSocketServerProtocol] = dict()
        self.__backend_caller = WebsocketBackendCaller(backend_strategy_repository,
                                                       redis, config,
                                                       self, response_bufferer)
        self.auth = Authenticator(config)

    def send_event_to_users(self, event: dict):
        print(event)
        try:
            signatures = event["signature"]
        except KeyError:
            return
        if type(signatures) is not list:
            signatures = [signatures]

        msg = json.dumps(event)
        with self.lock:
            for signature in signatures:
                try:
                    # Move this out of Main thread
                    asyncio.run(self.__user_usernames_to_websockets[signature].send(msg))
                except KeyError as e:
                    print(e)

    @staticmethod
    def __handle_api_call_request_timeout(websocket: WebSocketServerProtocol,
                                          request: dict):
        response = {
            "response_id": request["message_id"],
            "status": "failure",
            "cause": "Room hosting server timed out."
        }
        # TODO: get it out to another thread
        asyncio.run(websocket.send(json.dumps(response)))

    async def __handle_api_call_request(self, websocket: WebSocketServerProtocol,
                                        session: WebsocketSession,
                                        request: dict):
        if session.user is None:
            response = {
                "response_id": request["message_id"],
                "status": "failure",
                "cause": "Not logged in"
            }
            await websocket.send(json.dumps(response))
            return
        self.__backend_caller.call(request, session.user, 10,
                                   lambda: WebsocketService.__handle_api_call_request_timeout(websocket, request))

    async def __handle_login_request(self, websocket: WebSocketServerProtocol,
                                     session: WebsocketSession,
                                     request: dict):
        message_id = request.get("message_id")
        fields = ["username", "password"]
        for field in fields:
            if type(request.get(field)) is not str:
                response = {
                    "response_id": message_id,
                    "status": "failure",
                    "cause": f"Expected field {field} to have type str, found {type(request.get(field))} instead"
                }
                await websocket.send(json.dumps(response))
                return

        if session.user is None:
            session.user = self.auth.authenticate(request)

        if session.user is not None:
            response = {
                "response_id": message_id,
                "status": "success"
            }
            self.__user_usernames_to_websockets[session.user.username] = websocket
        else:
            response = {
                "response_id": message_id,
                "status": "failure",
                "cause": "Incorrect username or password."
            }
        await websocket.send(json.dumps(response))

    @staticmethod
    async def __handle_ill_formatted_message(websocket: WebSocketServerProtocol,
                                             session: WebsocketSession,
                                             invalid_message: str):
        session.ill_formatted_msgs_send = session.ill_formatted_msgs_send + 1
        if session.ill_formatted_msgs_send < 50:
            response = {
                "type": "invalid_message",
                "error": "Untagged or wrongly formatted message",
                "original_message": invalid_message
            }
            await websocket.send(json.dumps(response))
        else:
            response = {
                "type": "connection_closed",
                "error": "Invalid or outdated client."
            }
            await websocket.send(json.dumps(response))
            await websocket.close(reason="Invalid or outdated client.")

    async def __handle_request(self, websocket: WebSocketServerProtocol,
                               session: WebsocketSession,
                               request: dict):
        if type(request.get("type")) is not str:
            response = {
                "response_id": request["message_id"],
                "status": "failure",
                "cause": f"Expected field 'type' to have type str, found {type(request.get("type"))} instead"
            }
            await websocket.send(json.dumps(response))
            return

        type_ = request.get("type")
        if type_ == "login":
            await self.__handle_login_request(websocket, session, request)
        else:
            await self.__handle_api_call_request(websocket, session, request)

    def send_msg_to_user(self, msg: str | dict, username: str):
        if type(msg) is dict:
            msg = json.dumps(msg)

        with self.lock:
            try:
                asyncio.run(self.__user_usernames_to_websockets[username].send(msg)) # get this out of this thread
            except KeyError as e:
                print(e)

    async def __websocket_endpoint(self, websocket: WebSocketServerProtocol):
        session = WebsocketService.WebsocketSession()
        async for message in websocket:
            message_json = decode_json(message)
            message_type = check_message_type(message_json)

            if message_type == UserMessageType.request:
                await self.__handle_request(websocket, session, message_json)
            elif message_type == UserMessageType.event_response:
                pass  # TODO: handle event responses
            elif message_type == UserMessageType.ill_formatted:
                await self.__handle_ill_formatted_message(websocket, session, message)
        if session.user is not None:
            self.__user_usernames_to_websockets.pop(session.user.username)

    async def __service_main(self):
        async with serve(self.__websocket_endpoint,
                         host="localhost",
                         port=5001):
            await asyncio.Future()

    def run(self):
        asyncio.run(self.__service_main())
