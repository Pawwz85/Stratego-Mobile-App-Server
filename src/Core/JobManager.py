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
        """
        Represents a job that can be executed asynchronously.

        :param task: The callable function to execute when the job is run.
        """
        self.task = task
        self._JobManagerJobIteratorNode: None | LinkedList.LinkedListNode = None

    def __call__(self):
        """
             Executes the job's task synchronously.
        """
        self.task()

    def cancel(self):
        """
            Cancels the execution of this job and detaches it from the job manager's job iterator.
        """
        if self._JobManagerJobIteratorNode is not None:
            self._JobManagerJobIteratorNode.detach()


def time_ms() -> int:
    """
    That function returns time() value as integer amount of milliseconds
    :return: integer value of time in milliseconds
    """
    res_time = time()*1000
    return floor(res_time)


class DelayedTask:
    def __init__(self, task: Callable, delay: int):
        """
          Represents a delayed task that can be executed asynchronously after a specified delay.

          :param task: The callable function to execute when the task is run.
          :param delay: The number of milliseconds before the task should be executed.
        """
        self.__task = task
        self.__deadline = time_ms() + delay
        self._TaskPriorityQueue: None | PriorityQueue = None
        self._key = None

    def __call__(self):
        """
           Executes the delayed task's task asynchronously if its deadline has passed
        """
        if time_ms() > self.__deadline:
            self.__task()
            self.cancel()

    def get_deadline(self):
        """
           Returns the deadline for this delayed task in milliseconds.
        """
        return self.__deadline

    def cancel(self):
        """
            Cancels the execution of this delayed task and removes it from the priority queue
        :return:
        """
        if self._TaskPriorityQueue is not None:
            self._TaskPriorityQueue.remove(self._key)


class JobManager:
    """
    JobManager is a class designed to manage job execution and task scheduling using linked list and priority queue
    data structures. It provides methods for adding new jobs or tasks, killing all currently running jobs and tasks,
    iterating through the job execution process, and scheduling delayed tasks with priorities. The `__len__` method
    returns the total number of jobs and tasks in the manager.

    Attributes:
    - job_iterator (LinkedList): A linked list to store active jobs
    - task_queue (PriorityQueue): A priority queue to schedule delayed tasks

    """
    def __init__(self):
        self.job_iterator = LinkedList()
        self.task_queue = PriorityQueue()

    def __len__(self):
        return len(self.job_iterator) + len(self.task_queue)

    def add_job(self, job: Job):
        """
        Adds a new job to the job iterator of the manager. Each added job is assigned a node in the linked list.

        :param job: The job object to add to the manager's job iterator
        """
        job._JobManagerJobIteratorNode = self.job_iterator.add(job)

    def add_delayed_task(self, task: DelayedTask):
        """
        Adds a new delayed task with a deadline to the priority queue of the manager. Each added task is assigned a

        :param task: The delayed task object to schedule in the priority queue
        """
        task._TaskPriorityQueue = self.task_queue
        task._key = self.task_queue.add(-task.get_deadline(), task.__hash__(), task)

    def kill(self):
        """
        Cancels all currently running jobs and tasks in both the job iterator and priority queue.
        """
        for job in self.job_iterator:
            job.cancel()
        while self.task_queue.get_top() is not None:
            self.task_queue.get_top().cancel()

    def iteration_of_job_execution(self):
        """
        Iterates through the execution of all added jobs in the job iterator, followed by the delayed tasks with
        expired deadlines in the priority queue. This method should be called after all jobs and tasks have been
        added to the manager.
        """
        for job in self.job_iterator:
            job()

        exit_queue = False
        while not exit_queue:
            top: DelayedTask = self.task_queue.get_top()
            if top is not None and time_ms() > top.get_deadline():
                top()
            else:
                exit_queue = True
