from typing import Callable

from src.User import User


class _ChatMessage:
    def __init__(self, nickname: str, message: str):
        self.nickname = nickname
        self.message = message


class Chat:
    def __init__(self, event_broadcaster: Callable, max_size: int = 1024):
        self.messages: list[_ChatMessage | None] = [None] * max_size
        self.count = 0
        self._update_count = 0
        self.max_size = 1024
        self.event_broadcaster = event_broadcaster

    def __reset(self, survivor_count):

        for i in range(survivor_count):
            self.messages[i] = self.messages[i + self.max_size - survivor_count]

        self.messages[0] = _ChatMessage("system", "Chat reset.")
        self.count = survivor_count

        self._update_count += 1

        reset_event = {
            "type": "chat_reset",
            "messages": self.messages[0:survivor_count - 1]
        }
        self.event_broadcaster(reset_event)

    def add_message(self, msg: _ChatMessage):
        self.messages[self.count] = msg
        self.count += 1

        self._update_count += 1

        add_msg_event = {
            "type": "chat_event",
            "nr": self._update_count,
            "nickname": msg.nickname,
            "message": msg.message
        }
        self.event_broadcaster(add_msg_event)

        if self.count == self.max_size:
            self.__reset(self.max_size // 4)


class ChatApi:

    def __init__(self, chat: Chat):
        self.chat = chat

    def post_message(self, user: User, request: dict) -> tuple[bool, str | None]:
        message: str | None = request.get("message", None)
        if type(message) is not str:
            return False, f"Expected field message to have type of str, found {type(message)}"

        if len(message) > 2048:
            return False, "Message can not be longer than 2048 characters."

        msg = _ChatMessage(user.username, message)
        self.chat.add_message(msg)

        return True, None

    def get_chat_meta(self):
        return {
            "status": "success",
            "chat_metadata": {
                "size": self.chat.count
            }
        }

    def get_chat_messages(self, request: dict) -> dict | tuple[bool, str | None]:
        from_ = request.get("from")
        to_ = request.get("to")

        if type(from_) is not int:
            return False, f'Field "from" should have type of int, found {type(from_)} instead'

        if type(to_) is not int:
            return False, f'Field "to" should have type of int, found {type(from_)} instead'

        if from_ not in range(self.chat.count) or to_ not in range(self.chat.count):
            return False, 'Access out of range'

        return {
            "status": "success",
            "messages": self.chat.messages[from_: to_]
        }
