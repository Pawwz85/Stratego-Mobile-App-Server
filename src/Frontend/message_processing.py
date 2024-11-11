"""
    This Module aids to provide a functionality to ensure, that incoming user messages satisfy our format.
    This module only analyses the messages send by websocket clients
"""

import enum
import json
import time
from collections import deque
from threading import Lock


class UserMessageType(enum.Enum):
    """
    An enum used by MessageHandlingStrategyPicker to determine which strategy to use
    """
    ill_formatted = 0
    request = 1
    event_response = 2


def decode_json(raw_message: str) -> None | dict:
    """
    Parses raw_message into a python dict, returns None on failure.
    raw_message: message to parse
    """
    try:
        result = json.loads(raw_message)
        return result
    except json.decoder.JSONDecodeError:
        return None


def check_message_type(decoded_json: None | dict) -> UserMessageType:
    """
    Decides whatever message is untagged, request or response to a server event
    decoded_json: result of decode_json on some message
    """
    if decoded_json is None:
        return UserMessageType.ill_formatted

    if decoded_json.get("message_id", None) is not None:
        return UserMessageType.request
    elif decoded_json.get("response_id", None) is not None:
        return UserMessageType.event_response
    else:
        return UserMessageType.ill_formatted


class ResponseBufferer:
    """
    Class created to cache old server responses to allow application level retries
    """
    def __init__(self):
        self.response_buffer: dict[str, str] = dict()
        self._entry_last_interact: dict[str, float] = dict()
        self.entry_discard_time_s = 10.0

    def _remove_entry(self, response_id: str) -> None:
        self.response_buffer.pop(response_id)
        self._entry_last_interact.pop(response_id)

    def check_for_response(self, response_id: str) -> bool:
        return response_id in self.response_buffer.keys()

    def get_response(self, response_id: str) -> str | None:
        result = self.response_buffer.get(response_id)
        if result:
            print(self._entry_last_interact[response_id] - time.time())
            self._entry_last_interact[response_id] = time.time()

        return result

    def discard_old_entries(self):
        now = time.time()
        keys_to_remove = [key for key in self.response_buffer.keys()\
                          if now - self._entry_last_interact[key] > self.entry_discard_time_s]
        for key in keys_to_remove:
            self._remove_entry(key)

    def add_response(self, response_id: str, response: str):
        self.response_buffer[response_id] = response
        self._entry_last_interact[response_id] = time.time()


class UserResponseBufferer:
    def __init__(self):
        self.user_buffers: dict[str, ResponseBufferer] = dict()
        self.lock = Lock()

    def add_response(self, username: str, response_id: str, response: str):
        with self.lock:
            user_buffer = self.user_buffers.get(username)
            if user_buffer is None:
                user_buffer = ResponseBufferer()
                self.user_buffers[username] = user_buffer
            user_buffer.add_response(response_id, response)

    def create_placeholder_response(self, username: str, response_id: str):
        placeholder = {
            "status": "processing",
            "response_id": response_id,
            "timestamp": time.time()    # time stamp of creation of this placeholder
        }
        self.add_response(username, response_id, json.dumps(placeholder))

    def get_response(self, username: str, response_id: str):
        with self.lock:
            user_buffer = self.user_buffers.get(username)
            return None if user_buffer is None else user_buffer.get_response(response_id)

    @staticmethod
    def _check_for_timeout(response: dict, threshold: float) -> dict:
        if (timestamp := response.get("timestamp")) is not None:
            if timestamp + threshold < time.time():
                response["status"] = "timed out"

        return response

    def get_parsed_response(self, username: str, response_id: str):
        response = self.get_response(username, response_id)
        if response is not None:
            result: dict = json.loads(response)
            return self._check_for_timeout(result, 10)
        return None

    def discard_old_entries(self):
        with self.lock:
            to_remove = deque()
            for key, buffer in self.user_buffers.items():
                if len(buffer.response_buffer) > 0:
                    buffer.discard_old_entries()
                else:
                    to_remove.append(key)
            for key in to_remove:
                self.user_buffers.pop(key)
