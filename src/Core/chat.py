import json
from typing import Callable

from src.Core.User import User


class _ChatMessage:
    """
    A simple structure representing a chat message.

    :param nickname: Nickname of the message poster.
    :param message: Content of the message
    """
    def __init__(self, nickname: str, message: str):
        self.nickname = nickname
        self.message = message

    def to_json(self):
        return {
            "nickname": self.nickname,
            "message": self.message
        }


class Chat:
    def __init__(self, event_broadcaster: Callable, max_size: int = 1024):
        """
         A component representing chat.
         
        :param event_broadcaster: A callable that receives a dictionary and broadcast it to chat users
        :param max_size: A maximal amount of messages chat can have.
        """
        self._messages: list[_ChatMessage | None] = [None] * max_size
        self.__count = 0
        self._update_count = 0
        self._max_size = 1024
        self._event_broadcaster = event_broadcaster

    def __reset(self, survivor_count):
        """
        Shrinks chat to smaller size.

        :param survivor_count: Amount of latest messages preserved after reset
        :return: 
        """
        for i in range(survivor_count):
            self._messages[i] = self._messages[i + self._max_size - survivor_count]

        self._messages[0] = _ChatMessage("system", "Chat reset.")
        self.__count = survivor_count

        self._update_count += 1

        reset_event = {
            "type": "chat_reset",
            "messages": self._messages[0:(survivor_count - 1)]
        }
        self._event_broadcaster(reset_event)

    def add_message(self, msg: _ChatMessage):
        """
        Add new message to chat.

        :param msg: Message to add to chat.
        :return:
        """
        self._messages[self.__count] = msg
        self.__count += 1

        self._update_count += 1

        add_msg_event = {
            "type": "chat_event",
            "nr": self._update_count,
            "nickname": msg.nickname,
            "message": msg.message
        }
        self._event_broadcaster(add_msg_event)

        if self.__count >= self._max_size:
            self.__reset(self._max_size // 4)

    def __len__(self):
        return self.__count

    def __getitem__(self, item):
        return self._messages.__getitem__(item)

    def get_capacity(self):
        """
        A method that return maximum amount of messages chat can have, before automatically resetting itself
        :return: int
        """
        return self._max_size


class ChatApi:
    """
    An API interface of chat.

    Each method of following API:
        1) could take keyword "user" as an argument, this argument represents the user which is making the call
        2) could take keyword "request" as an argument, this argument represents the request user has sent to the server
        3) return either full response (dict) or status (tuple[bool, str | None])
        4) In case API call is returning status first argument of result is success flag while second is
        an optional string that explains why status is false, if status flag is True, then the second argument is None
    """
    def __init__(self, chat: Chat):
        self.chat = chat

    def post_message(self, user: User, request: dict) -> tuple[bool, str | None]:
        """
        :param user: A user on behalf with call is being make.
        :param request: An original request of the user
        :return: (True, None) if success, (False, {excuse}) otherwise
        """
        message: str | None = request.get("message", None)
        if type(message) is not str:
            return False, f"Expected field message to have type of str, found {type(message)}"

        if len(message) > 2048:
            return False, "Message can not be longer than 2048 characters."

        msg = _ChatMessage(user.username, message)
        self.chat.add_message(msg)

        return True, None

    def get_chat_meta(self):
        """
            :return: A json response containing chat_metadata
        """
        return {
            "status": "success",
            "chat_metadata": {
                "size": len(self.chat),
                "capacity": self.chat.get_capacity()
            }
        }

    def get_chat_messages(self, request: dict) -> dict | tuple[bool, str | None]:
        """
               :param request: An original request of the user
               :return: If success a json response containing the messages, (False, {excuse}) otherwise
        """
        from_ = request.get("from")
        to_ = request.get("to")

        if type(from_) is not int:
            return False, f'Field "from" should have type of int, found {type(from_)} instead'

        if type(to_) is not int:
            return False, f'Field "to" should have type of int, found {type(from_)} instead'

        if from_ not in range(len(self.chat)) or to_ not in range(len(self.chat) + 1):
            return False, 'Access out of range'

        return {
            "status": "success",
            "messages": self.chat[from_: to_]
        }
