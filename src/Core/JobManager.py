"""
    In this file are defined classes and functions that would allow us to
    control usage of server resources.
"""
from __future__ import annotations

from math import floor
from time import time
from typing import Callable

from src.DataStructures.PriorityQueue import PriorityQueue
from src.DataStructures.linked_list import LinkedList


class Job:
    def __init__(self, task: Callable):
        self.task = task
        self._ResourceManagerJobIteratorNode: None | LinkedList.LinkedListNode = None

    def __call__(self):
        self.task()

    def cancel(self):
        if self._ResourceManagerJobIteratorNode is not None:
            self._ResourceManagerJobIteratorNode.detach()


def time_ms() -> int:
    res_time = time()*1000
    return floor(res_time)


class DelayedTask:
    def __init__(self, task: Callable, delay: int):
        self.__task = task
        self.__deadline = time_ms() + delay
        self._TaskPriorityQueue: None | PriorityQueue = None
        self._key = None

    def __call__(self):
        if time_ms() > self.__deadline:
            self.__task()
            self.cancel()

    def get_deadline(self):
        return self.__deadline

    def cancel(self):
        if self._TaskPriorityQueue is not None:
            self._TaskPriorityQueue.remove(self._key)


class JobManager:

    def __init__(self):
        self.job_iterator = LinkedList()
        self.task_queue = PriorityQueue()

    def __len__(self):
        return len(self.job_iterator) + len(self.task_queue)

    def add_job(self, job: Job):
        job._ResourceManagerJobIteratorNode = self.job_iterator.add(job)

    def add_delayed_task(self, task: DelayedTask):
        task._TaskPriorityQueue = self.task_queue
        task._key = self.task_queue.add(-task.get_deadline(), task.__hash__(), task)

    def kill(self):
        for job in self.job_iterator:
            job.cancel()
        while self.task_queue.get_top() is not None:
            self.task_queue.get_top().cancel()

    def iteration_of_job_execution(self):
        for job in self.job_iterator:
            job()

        exit_queue = False
        while not exit_queue:
            top: DelayedTask = self.task_queue.get_top()
            if top is not None and time_ms() > top.get_deadline():
                top()
            else:
                exit_queue = True
