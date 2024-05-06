"""
    This Module aids to provide a functionality to ensure, that incoming user messages satisfy our format.
"""

import enum
import json
import time
from typing import Callable


class _UserMessageType(enum.Enum):
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


def _check_message_type(decoded_json: None | dict) -> _UserMessageType:
    """
    Decides whatever message is untagged, request or response to a server event
    decoded_json: result of decode_json on some message
    """
    if decoded_json is None:
        return _UserMessageType.ill_formatted

    if decoded_json.get("message_id", None) is not None:
        return _UserMessageType.request
    elif decoded_json.get("response_id", None) is not None:
        return _UserMessageType.event_response
    else:
        return _UserMessageType.ill_formatted


class ResponseBufferer:
    """
    Class created to cache old server responses to allow application level retries
    """
    def __init__(self):
        self._response_buffer: dict[str, str] = dict()
        self._entry_last_interact: dict[str, float] = dict()
        self.entry_discard_time_s = 10.0

    def _remove_entry(self, response_id: str) -> None:
        self._response_buffer.pop(response_id)
        self._entry_last_interact.pop(response_id)

    def check_for_response(self, response_id: str) -> bool:
        return response_id in self._response_buffer.keys()

    def get_response(self, response_id: str) -> str | None:
        self._entry_last_interact[response_id] = time.process_time()
        return self._response_buffer[response_id]

    def discard_old_entries(self):
        # This method is supposed to be run periodically
        now = time.process_time()
        for key in self._response_buffer.keys():
            if now - self._entry_last_interact[key] > self.entry_discard_time_s:
                self._remove_entry(key)


class MessageHandlingStrategy:

    def __init__(self, procedure: Callable):
        self.procedure = procedure

    def __call__(self, *args, **kwargs):
        return self.procedure(*args, **kwargs)


class MessageHandlingStrategyPicker:
    """
    Overall, this class provides a centralized system for selecting appropriate handling strategies based on message
    types, statuses, and other relevant factors. This approach allows for more flexible and customizable handling
    logic to be implemented in future iterations of this system without needing to modify existing code blocks.
    """
    def __init__(self, response_bufferer: ResponseBufferer):
        self.__request_handling_strategies: dict[str, MessageHandlingStrategy] = dict()
        self.__event_response_handling_strategies: dict[str, MessageHandlingStrategy] = dict()
        self._response_bufferer = response_bufferer

        self.send: Callable[[str], any] = print

    def _pick_strategy_for_request(self, message_json) -> MessageHandlingStrategy:
        """
            This method simply chooses the valid strategy for the received message.

            If message was already responded by a server, server would simply respond with a previous response.
            Otherwise, a strategy would be chosen accordingly to the request type.
        """
        if self._response_bufferer.check_for_response(message_json["message_id"]):
            return self._create_send_response_strategy(
                    self._response_bufferer.get_response(message_json["message_id"])
            )

        if message_json["type"] is None:
            return self._create_type_field_absent_strategy(message_json["message_id"])

        if message_json["type"] in self.__request_handling_strategies.keys():
            return self.__request_handling_strategies[message_json["type"]]
        else:
            return self._create_unexisting_type_strategy(message_json["message_id"], message_json["type"])

    def _pick_strategy_for_event_response(self, message_json) -> MessageHandlingStrategy:
        res_id = message_json["response_id"]
        if res_id in self.__event_response_handling_strategies.keys():
            result = self.__event_response_handling_strategies[res_id]
            self.__event_response_handling_strategies.pop(res_id)
            return result

        # return "Do nothing" strategy if we don't have a plan to react to this message
        return MessageHandlingStrategy(lambda: None)

    def pick(self, raw_message: str) -> tuple[MessageHandlingStrategy, None | dict]:

        message_json = decode_json(raw_message)
        message_type = _check_message_type(message_json)
        if message_type is _UserMessageType.ill_formatted:
            return self._create_ill_formatted_message_strategy(raw_message), message_json
        elif message_type is _UserMessageType.event_response:
            return self._pick_strategy_for_request(message_json), message_json
        else:
            return self._pick_strategy_for_event_response(message_json), message_json

    def _create_send_response_strategy(self, message: str) -> MessageHandlingStrategy:
        return MessageHandlingStrategy(lambda *args, **kwargs: self.send(message))

    def _create_type_field_absent_strategy(self, message_id) -> MessageHandlingStrategy:
        result = dict()
        result["status"] = "error"
        result["response_id"] = message_id
        result["error"] = f"\"type\" field is missing"
        return self._create_send_response_strategy(json.dumps(result))

    def _create_ill_formatted_message_strategy(self, raw_message: str) -> MessageHandlingStrategy:
        result = dict()
        result["type"] = "invalid_message"
        result["error"] = "Untagged or wrongly formatted message"
        result["original_message"] = raw_message
        return self._create_send_response_strategy(json.dumps(result))

    def _create_unexisting_type_strategy(self, message_id: str, request_type: str) -> MessageHandlingStrategy:
        result = dict()
        result["status"] = "error"
        result["response_id"] = message_id
        result["error"] = f"Server do not support {request_type} request"
        return self._create_send_response_strategy(json.dumps(result))
