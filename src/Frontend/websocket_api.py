from collections.abc import Callable
from dataclasses import dataclass

from src.Authenticathion.Authenticator import Authenticator
from src.Core.User import UserIdentity
from src.Frontend.message_processing import decode_json, check_message_type, UserMessageType
from src.Frontend.socket_manager import IUserSocket, SocketManager
from src.InterClusterCommunication.HandleGameNodeMessage import GameNodeAPIHandler


@dataclass
class WebsocketInfo:
    socket: IUserSocket
    user: UserIdentity | None  # None in case of users before login


class WebsocketStream:

    def __init__(self, api_handler: GameNodeAPIHandler, authenticator: Authenticator, socket_manager: SocketManager):
        self._game_node_message_handler = api_handler
        self._auth = authenticator
        self._socket_manager: SocketManager = socket_manager

    def _answer_request_from_unauthorised_user(self, request: dict, websocket: WebsocketInfo, callback: Callable[[dict], any]):
        allowed_types = ["login", "register"]
        request_type = request.get("type")

        if request_type not in allowed_types:
            response_body = {"status": "failure", "cause": "You must be logged to do that",
                             "response_id": request.get("message_id")}
            callback(response_body)
        elif request_type == "login":
            response_body = self._make_login_response(request, websocket)
            callback(response_body)
        elif request_type == "register":
            pass

    def _answer_request_from_authorised_user(self, request: dict, websocket: WebsocketInfo, callback: Callable[[dict], any]):

        # forward request to game api
        self._game_node_message_handler.on_user_request_dict(websocket.user, request, lambda _, res: callback(res))

    def _answer_request(self, request: dict, websocket: WebsocketInfo, callback: Callable[[dict], any]):
        if websocket.user:
            self._answer_request_from_authorised_user(request, websocket, callback)
        else:
            self._answer_request_from_unauthorised_user(request, websocket, callback)

    @staticmethod
    def _answer_wrongly_formatted_message(request: str, callback: Callable[[dict], any]):
        response_body = {
          "type": "invalid_message",
          "error": "Untagged or wrongly formatted message",
          "original_message": request
        }
        callback(response_body)

    def handle_request(self, request: str, websocket: WebsocketInfo):
        msg_json: dict | None = decode_json(request)
        msg_type: UserMessageType = check_message_type(msg_json)
        if msg_type is UserMessageType.request:
            self._answer_request(msg_json, websocket, websocket.socket.emit)
        elif msg_type is UserMessageType.event_response:
            pass
        elif msg_type is UserMessageType.ill_formatted:
            self._answer_wrongly_formatted_message(request, websocket.socket.emit)

    def _make_login_response(self, request, websocket: WebsocketInfo):
        websocket.user = self._auth.authenticate(request)
        response_body = {
            "status": "failure",
            "cause": "Incorrect credentials",
            "response_id": request.get("message_id")
        } if not websocket.user \
            else {
            "status": "success",
            "response_id": request.get("message_id")
        }
        print("Websocket.user=", websocket.user if websocket.user else "None")
        if websocket.user:
            websocket.socket.username = websocket.user.username
            self._socket_manager.register_entry(websocket.socket)

        return response_body
