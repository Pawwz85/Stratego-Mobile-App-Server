import threading
import time

from flask_socketio import SocketIO
from flask import Flask


class _SocketManagerEntry:
    def __init__(self, username: str, session_id: str | int):
        self.username = username
        self.sid = session_id
        self.last_touched = time.time()

    def touch(self):
        self.last_touched = time.time()


class SocketManager:
    def __init__(self):
        self.__entries: dict[str, _SocketManagerEntry] = dict()
        self.remember_time = 7200  # nr of seconds given session has to remembered after last board event
        self.lock = threading.Lock()

    def register_entry(self, username: str, session: str):
        with self.lock:
            self.__entries[username] = _SocketManagerEntry(username, session)

    def remove_old_entries(self):
        with self.lock:
            old_keys = [e.username for e in self.__entries.values()
                        if e.last_touched + self.remember_time < time.time()]

            for key in old_keys:
                self.__entries.pop(key)

    def get_session_id(self, username: str):
        with self.lock:
            result_entry = self.__entries.get(username)
            result = None if result_entry is None else (result_entry.sid, result_entry.touch())[0]
        return result


def send_event_to_socketio_clients(app: SocketIO, event: dict):
    signatures: list[str] = event["signature"]
    e = event.copy()
    e.pop("signature")
    print("ev", event)
    for sign in signatures:
        app.emit(e.get("type", "response"), e, namespace='/', to=sign)


def send_event_to_user(app: SocketIO, e: dict, username: str):
    app.emit(e.get("type", "response"), e, namespace='/', to=username)
