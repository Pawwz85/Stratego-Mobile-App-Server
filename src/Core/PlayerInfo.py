from __future__ import annotations
import time
from collections.abc import Callable
from enum import Enum
from math import floor

from src.Core.JobManager import DelayedTask
from src.Core.User import User


class TimerMode(Enum):
    PAUSED = 0,
    COUNT_DOWN = 1


class Timer:
    """
        A class used to store timer values.

        If timer mode is PAUSED, the value represents amount of milliseconds to 0.
        For example, if value is 62000, the timer UI should show 62000 milliseconds.

        If timer mode is COUNT_DOWN, the value represents a certain date in milliseconds (Epoch Time).
        This date represents the time when the timer UI should show 0.

    """
    def __init__(self, on_change: Callable = lambda: None):
        self.mode = TimerMode.PAUSED
        self.value: int = 0
        self.onChange = on_change
        self.__last_task: DelayedTask | None = None

    def __sync_task_with_timer(self, func: Callable) -> Callable:
        def _(*args, **kwargs):
            self.mode = TimerMode.PAUSED
            self.value = 0
            self.onChange()
            func(*args, **kwargs)
        return _

    def stop(self):
        if self.__last_task is not None:
            self.__last_task.cancel()
            self.__last_task = None
            self.mode = TimerMode.PAUSED
            self.value = 0

    def count_down(self, time_ms, on_time_runs_down: Callable) -> DelayedTask:
        self.stop()
        self.mode = TimerMode.COUNT_DOWN
        self.value = floor(1000*time.time()) + time_ms
        self.onChange()
        result = DelayedTask(on_time_runs_down, time_ms)
        result.cancel = self.__sync_task_with_timer(result.cancel)
        self.__last_task = result
        return result

    def set_paused_value(self, time_ms):
        self.stop()
        self.mode = TimerMode.PAUSED
        self.value = time_ms
        self.onChange()

    def to_dict(self) -> dict[str, str | int]:
        return {
            "mode": "paused" if self.mode is TimerMode.PAUSED else "count_down",
            "value": self.value
        }


class PlayerInfo:
    """
        A class that aggregates information about the player in stratego.

        The tracked information include:
        - Player Username
        - Timer Mode
        - Timer Value
    """
    def __init__(self):
        self.user_id: int | None = None  # This field shouldn't be exposed in our API, only internal server usage
        self.username: str | None = None
        self.timer: Timer = Timer(self.__notify_observers)
        self.__observers: list[Callable[[PlayerInfo], any]] = []

    def add_observers(self, callback: Callable[[PlayerInfo], any]):
        self.__observers.append(callback)

    def __notify_observers(self):
        for o in self.__observers:
            o(self)

    def to_dict(self) -> dict:
        """
        Represents Player Info in the way that is ready to be converted to json
        :return:
        """

        return {
            "username": self.username,
            "timer": self.timer.to_dict()
        }

    def set_user(self, user: User | None):
        if user is None:
            self.user_id = self.username = None
        else:
            self.user_id = user.id
            self.username = user.username

        self.__notify_observers()

