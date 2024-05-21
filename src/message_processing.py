"""
    This Module aids to provide a functionality to ensure, that incoming user messages satisfy our format.
    This module only analyses the messages send by websocket clients
"""

import enum
import json
import time
from threading import Lock
from typing import Callable


class UserMessageType(enum.Enum):
    """
    An enum used by MessageHandlingStrategyPicker to determine which strategy to use
    """
    ill_formatted: 0
    request: 1
    event_response: 2


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
        self.lock = Lock()
        self._response_buffer: dict[str, str] = dict()
        self._entry_last_interact: dict[str, float] = dict()
        self.entry_discard_time_s = 10.0

    def _remove_entry(self, response_id: str) -> None:
        with self.lock:
            self._response_buffer.pop(response_id)
            self._entry_last_interact.pop(response_id)

    def check_for_response(self, response_id: str) -> bool:
        with self.lock:
            return response_id in self._response_buffer.keys()

    def get_response(self, response_id: str) -> str | None:
        with self.lock:
            self._entry_last_interact[response_id] = time.process_time()
            return self._response_buffer[response_id]

    def discard_old_entries(self):
        # This method is supposed to be run periodically
        with self.lock:
            now = time.process_time()
            for key in self._response_buffer.keys():
                if now - self._entry_last_interact[key] > self.entry_discard_time_s:
                    self._remove_entry(key)

    def add_response(self, response_id: str, response: str):
        with self.lock:
            self._response_buffer[response_id] = response
            self._entry_last_interact[response] = time.process_time()
