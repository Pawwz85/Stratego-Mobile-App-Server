import json
from collections import deque
from collections.abc import Callable
from threading import Thread, Lock
from typing import Deque

from src.Core.JobManager import JobManager
from src.Core.Room import IRoomHandle
from src.Core.User import UserDto
from src.Events.Events import IEventReceiver, Eventmanager
from src.GameNode.GameManager import GameManager
from src.GracefulThreads import GracefulThread, loop_forever_gracefully

"""
    TODO:
    1. Add a callbacks that schedule "routing" to our channel by room name
    2. Configure Node to be runnable
    3. On boot add this node to register its private channel, and unregister on shutdown
"""


class QueueEventReceiver(IEventReceiver):

    def __init__(self, on_disconnect: Callable, event_man: Eventmanager):
        super().__init__(on_disconnect)
        self._lock = Lock()
        self._event_man = event_man
        self._queue: deque[str] = deque()

    def receive(self, message: str):
        with self._lock:
            self._queue.append(message)
        event_body = json.loads(message)
        event_id = event_body["event_id"]
        self._event_man.event_delivered(event_id)

    def copy_and_clear(self):
        with self._lock:
            result = self._queue.copy()
            self._queue.clear()
        return result


@GracefulThread
class GameManagerThread(Thread):

    def __init__(self, room_handle_factory: Callable[[], IRoomHandle],
                 enable_privileged_testing_mode: bool = False):
        super().__init__()
        self._job_manager: JobManager = JobManager()
        self._event_receiver_factory = lambda event_man: QueueEventReceiver(lambda: None, event_man)
        self._out_queue: Deque[str] = deque()
        self._out_lock = Lock()
        self._in_deque: Deque[str] = deque()
        self._in_lock = Lock()

        self._game_manager = GameManager(self._job_manager, self._event_receiver_factory, room_handle_factory,
                                         enable_privileged_testing_mode=enable_privileged_testing_mode)
        self._game_manager.schedule_periodic_user_garbage_collection()
        self._event_receiver = self._game_manager.eventReceiver

    def _read_from_in(self):
        with self._in_lock:
            result = self._in_deque.copy()
            self._in_deque.clear()
        return result

    def write_request(self, request: str):
        with self._in_lock:
            self._in_deque.append(request)

    def retrieve_responses_and_events(self):
        result = self._event_receiver.copy_and_clear()
        result.extend(self._copy_and_clear_out_queue())
        return result

    def _write_to_out(self):
        with self._out_lock:
            self._out_queue.extend(self._event_receiver.copy_and_clear())

    def _copy_and_clear_out_queue(self):
        with self._out_lock:
            result = self._out_queue.copy()
            self._out_queue.clear()
        return result

    @staticmethod
    def parse_request(message: str) -> tuple[UserDto, dict]:
        js = json.loads(message)
        user_json: dict = js["user"]
        user_dto = UserDto(user_json["username"], user_json["password"], user_json["user_id"])
        request: dict = js["request"]
        return user_dto, request

    def _iterate_requests(self):
        reqs = self._read_from_in()
        out: deque[str] = deque()
        for req in reqs:
            user_dto, request_body = GameManagerThread.parse_request(req)
            self._game_manager.register_user(user_dto)
            user = self._game_manager.users_connected[user_dto.user_id]
            response = self._game_manager.api(user, request_body)
            if response is not None:
                response["response_id"] = request_body["message_id"]
                out.append(json.dumps(response))
        return out

    @loop_forever_gracefully
    def run(self):

        responses = self._iterate_requests()
        with self._out_lock:
            self._out_queue.extend(responses)
        self._job_manager.iteration_of_job_execution()
        self._write_to_out()

    def stop(self):  # this method implementation is injected by @GracefulThread decorator
        pass
