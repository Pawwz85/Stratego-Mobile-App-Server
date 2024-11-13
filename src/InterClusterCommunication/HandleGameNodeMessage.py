import json
from typing import Callable

from src.AsyncioWorkerThread import AsyncioWorkerThread
from src.Core.User import UserDto
from src.Frontend.IntermediateRequestIDMapper import IntermediateRequestIDMapper
from src.Frontend.message_processing import UserResponseBufferer, decode_json, check_message_type, UserMessageType
from src.InterClusterCommunication.IEventChannelManager import IChannelManager


class _MissingFieldRoomID(Exception):
    pass


class GameNodeAPIHandler:

    def __init__(self,
                 mapper: IntermediateRequestIDMapper,
                 response_bufferer: UserResponseBufferer,
                 channel_manager: IChannelManager,
                 worker_thread: AsyncioWorkerThread,
                 broadcast_events_to_users: Callable[[dict], any]):
        self._request_mapper = mapper
        self._user_response_buffer = response_bufferer
        self._channel_manager = channel_manager
        self._worker_thread = worker_thread
        self._broadcast_events_to_users = broadcast_events_to_users

    def handle_game_node_message(self, msg: str):

        print(f"Received message: {msg}")
        try:
            msg_json = json.loads(msg)
        except json.JSONDecodeError as e:
            print(e)
            return None

        response_id = msg_json.get("response_id", None)
        print(msg_json)
        if response_id is None:
            self._broadcast_events_to_users(msg_json)
            return None

        entry = self._request_mapper.match_entry_to_response(msg_json)
        print(entry, entry.user_username if entry else "Joe")
        if entry is not None:
            msg_json["response_id"] = entry.original_id
            print(f"org id: {entry.original_id}, new_id: {entry.new_id}")
            self._user_response_buffer.add_response(entry.user_username, entry.original_id, msg)

            if entry.callback is not None:
                entry.callback(entry.user_username, msg_json)
            else:
                print("Missing callback argument")

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

    async def _submit_browse_room_command(self, user: UserDto, request: dict):
        ch = request.get("channel", "default")
        msg = {
            "user": {"username": user.username, "user_id": user.user_id, "password": user.password},
            "request": request
        }
        await self._channel_manager.get_pub_sub().publish(ch, json.dumps(msg))

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

    def on_user_request(self, user: UserDto, request: str | dict,
                        callback: Callable[[str, dict], any]):
        request_json = decode_json(request) if type(request) is str else request
        self.on_user_request_dict(user, request_json, callback=callback)

    def on_user_request_dict(self, user: UserDto, request_json: dict | None, callback: Callable[[str, dict], any],
                             request: str | None = None):
        request_type = check_message_type(request_json)
        request = json.dumps(request_json) if request is None else request
        if request_type is UserMessageType.ill_formatted:
            result = self._create_response_for_untagged_message(request)
            callback(user.username, result)
        elif request_type is UserMessageType.event_response:
            pass
        elif request_type is UserMessageType.request:

            cached_response = self._user_response_buffer.get_response(user.username, request_json["message_id"])
            print(f"Cached response: {cached_response} for {user.username}, req_id: {request_json["message_id"]}")
            if cached_response is not None:
                callback(user.username, json.loads(cached_response))
                return

            self.send_request(callback, request_json, user)

    def send_request(self, callback: Callable[[str, dict], any] | None, request: dict, user: UserDto):
        request_id = request.get("message_id")

        if not request_id:
            result = self._create_response_for_untagged_message(json.dumps(request))
            callback(user.username, result)
            return

        self.create_placeholder_response(request_id, user)
        request = self._request_mapper.assign_intermediate_request(user.username, request, callback)

        try:
            self._forward_request_to_game_node_(request, user)
        except _MissingFieldRoomID:
            result = self._create_room_id_missing_response(request_id)
            callback(user.username, result)

    def _forward_request_to_game_node_(self, request: dict, user: UserDto):
        if request.get("type") == "create_room":
            self._worker_thread.add_task(self._submit_create_room_command(user, request))
        elif request.get("type") == "browse_rooms":
            self._worker_thread.add_task(self._submit_browse_room_command(user, request))
        elif (room_id := request.get("room_id")) is not None:
            self._worker_thread.add_task(self._submit_by_room(user, room_id, request))
        else:
            raise _MissingFieldRoomID()

    def create_placeholder_response(self, request_id: str, user: UserDto):
        self._user_response_buffer.create_placeholder_response(user.username, request_id)

    def probe_response(self, user: UserDto, request_id: str) -> dict | None:
        raw_res = self._user_response_buffer.get_response(user.username, request_id)
        return json.loads(raw_res) if raw_res else None
