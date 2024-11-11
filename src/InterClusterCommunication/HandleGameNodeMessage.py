import json

from flask_socketio import SocketIO

from src.AsyncioWorkerThread import AsyncioWorkerThread
from src.Core.User import UserDto
from src.Frontend.IntermediateRequestIDMapper import IntermediateRequestIDMapper
from src.Frontend.message_processing import UserResponseBufferer, decode_json, check_message_type, UserMessageType
from src.Frontend.socketio_socket_management import send_event_to_socketio_clients, send_event_to_user
from src.InterClusterCommunication.IEventChannelManager import IChannelManager


# TODO: add support for websocket clients
class GameNodeAPIHandler:

    def __init__(self,
                 app: SocketIO,
                 mapper: IntermediateRequestIDMapper,
                 response_bufferer: UserResponseBufferer,
                 channel_manager: IChannelManager,
                 worker_thread: AsyncioWorkerThread):
        self._app = app
        self._request_mapper = mapper
        self._user_response_buffer = response_bufferer
        self._channel_manager = channel_manager
        self._worker_thread = worker_thread

    def HandleGameNodeMessage(self, msg: str):

        print(f"Received message: {msg}")
        try:
            msg_json = json.loads(msg)
        except json.JSONDecodeError as e:
            print(e)
            return None

        response_id = msg_json.get("response_id", None)

        if response_id is None:
            send_event_to_socketio_clients(self._app, msg_json)
            return None

        entry = self._request_mapper.match_entry_to_response(msg_json)
        print(entry)

        if entry is not None:
            msg_json["response_id"] = entry.original_id
            self._user_response_buffer.add_response(entry.user_username, entry.original_id, msg)
            send_event_to_user(self._app, msg_json, entry.user_username)

    @staticmethod
    def _create_response_for_untagged_message(msg: str):
        return {
                "type": "invalid_message",
                "error": "Untagged or wrongly formatted message",
                "original_message": msg
            }

    @staticmethod
    def _create_room_id_missing_response(response_id: str):
        return {
            "type": "error",
            "response_id": response_id,
            "error": "Missing value \"room_id\"",
        }

    async def _submit_create_room_command(self, user: UserDto, request: dict):
        msg = {
            "user": {"username": user.username, "user_id": user.user_id, "password": user.password},
            "request": request
        }
        await self._channel_manager.get_request_queue().enqueue_request(json.dumps(msg))

    async def _submit_by_room(self, user: UserDto, room_id: str, request: dict):
        channel = await self._channel_manager.get_routing_manager().get_routing(room_id)
        print(f"Room {room_id} is available on {channel}")
        msg = {
            "user": {"username": user.username, "user_id": user.user_id, "password": user.password},
            "request": request
        }

        if channel is not None:
            await self._channel_manager.get_pub_sub().publish(channel, json.dumps(msg))
        else:
            pass
            # TODO: tell user that there is no such room

    def on_user_request(self, user: UserDto, request: str | dict):
        request_json = decode_json(request) if type(request) is str else request
        self.on_user_request_dict(user, request_json)

    def on_user_request_dict(self, user: UserDto, request_json: dict | None, request: str | None = None):
        request_type = check_message_type(request_json)

        request = json.dumps(request_json) if request is None else request

        if request_type is UserMessageType.ill_formatted:
            result = self._create_response_for_untagged_message(request)
            send_event_to_user(self._app, result, user.username)
        elif request_type is UserMessageType.event_response:
            pass
        elif request_type is UserMessageType.request:
            cached_response = self._user_response_buffer.get_response(user.username, request_json["message_id"])

            if cached_response is not None:
                send_event_to_user(self._app, json.loads(cached_response), user.username)
                return

            request_id = request_json["message_id"]
            self._user_response_buffer.create_placeholder_response(user.username, request_id)
            request_json = self._request_mapper.assign_intermediate_request(user.username, request_json)
            if request_json.get("type") == "create_room":
                self._worker_thread.add_task(self._submit_create_room_command(user, request_json))
            elif (room_id := request_json.get("room_id")) is not None:
                self._worker_thread.add_task(self._submit_by_room(user, room_id, request_json))
            else:
                result = self._create_room_id_missing_response(request_id)
                send_event_to_user(self._app, result, user.username)