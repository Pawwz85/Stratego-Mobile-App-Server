import uuid
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class _IntermediateRequestEntry:
    original_id: str
    new_id: str
    user_username: str
    callback: Callable[[str, dict], any] | None


# TODO: clear old or timed out entries
class IntermediateRequestIDMapper:
    def __init__(self):
        self.__wrapped_requests: dict[str, _IntermediateRequestEntry] = dict()

    def get_id(self, id_: str):
        return self.__wrapped_requests.get(id_)

    @staticmethod
    def _generate_uuid():
        return uuid.uuid4().hex

    def assign_intermediate_request(self, username: str, request: dict, callback: Callable[[str, dict], any] | None):
        original_id = request.get("message_id")
        new_id = self._generate_uuid()
        request["message_id"] = new_id
        self.__wrapped_requests[new_id] = _IntermediateRequestEntry(original_id, new_id, username, callback)
        return request

    def match_entry_to_response(self, response: dict):
        return self.__wrapped_requests.get(response["response_id"])
