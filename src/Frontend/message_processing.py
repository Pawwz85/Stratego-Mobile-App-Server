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


class TimeConstrainedRecord:
    def __init__(self, data: any, discard_time_s: float = 10, refresh_on_touch: bool = True):
        self._data = data
        self._last_interact: float = time.time()
        self._discard_time: float = discard_time_s
        self._refresh_on_touch: bool = refresh_on_touch

    def touch(self):
        if self._refresh_on_touch:
            self._last_interact = time.time()

    def is_old(self, now: float | None = None):
        if now is None:
            now = time.time()
        return now - self._last_interact > self._discard_time

    def get_data(self):
        self.touch()
        return self._data


class ResponseBufferer:
    """
    Class created to cache old server responses to allow application level retries
    """
    def __init__(self, default_discard_time=10.0):
        self._entries: dict[str, TimeConstrainedRecord] = dict()
        self.entry_discard_time_s = default_discard_time

    def _remove_entry(self, response_id: str) -> None:
        self._entries.pop(response_id)

    def check_for_response(self, response_id: str) -> bool:
        return response_id in self._entries.keys()

    def get_response(self, response_id: str) -> str | None:
        result = self._entries.get(response_id)
        return result.get_data() if result else None

    def discard_old_entries(self):
        now = time.time()
        keys_to_remove = [key for key, record in self._entries.items()
                          if record.is_old(now)]
        for key in keys_to_remove:
            self._remove_entry(key)

    def __len__(self):
        return len(self._entries)

    def add_response(self, response_id: str, response: str,
                     discard_time: float | None = None,
                     refresh_on_touch: bool = True):
        discard_time = self.entry_discard_time_s if discard_time is None else discard_time
        self._entries[response_id] = TimeConstrainedRecord(response, discard_time, refresh_on_touch)


class UserResponseBufferer:
    def __init__(self):
        self.user_buffers: dict[str, ResponseBufferer] = dict()
        self.lock = Lock()

    def add_response(self, username: str, response_id: str, response: str,
                     discard_time: float | None = None,
                     refresh_on_touch: bool = True
                     ):
        with self.lock:
            user_buffer = self.user_buffers.get(username)
            if user_buffer is None:
                user_buffer = ResponseBufferer()
                self.user_buffers[username] = user_buffer
            user_buffer.add_response(response_id, response, discard_time, refresh_on_touch)

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
                if len(buffer) > 0:
                    buffer.discard_old_entries()
                else:
                    to_remove.append(key)
            for key in to_remove:
                self.user_buffers.pop(key)
