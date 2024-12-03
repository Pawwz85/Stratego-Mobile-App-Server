import json
import threading
import time
from abc import ABC, abstractmethod
from enum import Enum
from flask_socketio import SocketIO
from websockets.asyncio.server import ServerConnection

from src import AsyncioWorkerThread


class SocketType(Enum):
    SOCKETIO = 1
    WEBSOCKET = 2


class IUserSocket(ABC):
    def __init__(self, type_: SocketType, username: str):
        self._socket_type = type_
        self.username: str = username
        self._closed = False
        self.last_touched = time.time()

    def touch(self):
        self.last_touched = time.time()

    @abstractmethod
    def _close(self):
        pass

    def close(self):
        self._closed = True
        self._close()

    @abstractmethod
    def emit(self, event: dict):
        pass

    def is_closed(self):
        return self._closed


class SocketioUserSocket(IUserSocket):

    def __init__(self, username: str, app: SocketIO):
        super().__init__(SocketType.SOCKETIO, username)
        self.app = app

    def emit(self, event: dict):
        if not self.is_closed():
            self.app.emit(event.get("type", "response"), event, namespace='/', to=self.username)

    def _close(self):
        pass


class WebsocketUserSocket(IUserSocket):
    def __init__(self, username: str, socket: ServerConnection, worker: AsyncioWorkerThread.AsyncioWorkerThread):
        super().__init__(SocketType.WEBSOCKET, username)
        self.socket = socket
        self.worker = worker

    def emit(self, event: dict):
        if not self.is_closed():
            self.worker.add_task(self.socket.send(json.dumps(event), text=True))

    def _close(self):
        self.socket.close()


class UserSocketSet:
    def __init__(self):
        self._socket_set: set[IUserSocket] = set()

    def get_socket_set(self) -> set[IUserSocket]:
        return self._socket_set

    def remove_old_entries(self, remember_time: float):
        old_entries = {e for e in self._socket_set
                       if e.last_touched + remember_time < time.time() or e.is_closed()}

        for e in old_entries:
            e.close()

        self._socket_set.difference_update(old_entries)

    def emit(self, e: dict):
        for socket in self._socket_set:
            socket.emit(e)


class SocketManager:
    def __init__(self):
        self.__entries: dict[str, UserSocketSet] = dict()
        self.remember_time = 7200  # nr of seconds given session has to remembered after last board event
        self.lock = threading.Lock()

    def register_entry(self, sock: IUserSocket):
        with self.lock:
            if not self.__entries.get(sock.username):
                self.__entries[sock.username] = UserSocketSet()

            self.__entries[sock.username].get_socket_set().add(sock)

    def remove_old_entries(self):
        with self.lock:
            socket_set: UserSocketSet
            for socket_set in self.__entries.values():
                socket_set.remove_old_entries(self.remember_time)

            self.__entries = {k: v for k, v in self.__entries.items() if len(v.get_socket_set()) > 0}

    def emit_event_by_signature(self, event: dict):
        try:
            signatures: list[str] = event["signature"]
            e = event.copy()
            e.pop("signature")
            print("ev", event)
            for sign in signatures:
                sock = self.__entries.get(sign)
                if sock:
                    sock.emit(e)
        except KeyError:
            print("Failed to sent an event by signature, because signature is missing")

    def get_socket(self, username: str):
        set_ = self.__entries.get(username)
        return [s for s in set_.get_socket_set()][0] if set_ else None
