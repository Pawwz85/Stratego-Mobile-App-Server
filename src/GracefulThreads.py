"""
    The term "Graceful thread" is a thread that can be stopped gracefully
"""
import threading
import warnings
from typing import Callable


class _GracefulCallable:
    """
        A base class for all graceful decorators
    """

    def __init__(self, foo: Callable):
        self.hook = None  # A hook to a parent class
        self.function = foo
        self._set_kill = threading.Event()
        self._inside_graceful_thread = False  # safeguard against calling this outside of GracefulThread

    def _warm_user(self):
        if not self._inside_graceful_thread:
            warnings.warn("A gracefully Callable was run outside of graceful thread"
                          "Missing @GracefulThread decorator?")

    def __call__(self, *args, **kwargs):
        if self.hook is None:
            self._warm_user()
        self.function(self.hook, *args, **kwargs)


class _GracefulThread(threading.Thread):
    def __init__(self, target: _GracefulCallable | Callable):
        if type(target is _GracefulCallable):
            self.run: _GracefulCallable = target
        elif target is not None:
            self.run = _GracefulCallable(target)
            warnings.warn("No graceful decorator around run() method.")
        self.run._inside_graceful_thread = True

    def stop(self):
        print(self.run)
        self.run._set_kill.set()


class __GracefulInfiniteLoop(_GracefulCallable):
    def __call__(self, *args, **kwargs):
        if self.hook is None:
            self._warm_user()
        while not self._set_kill.is_set():
            self.function(self.hook, *args, **kwargs)


def loop_forever_gracefully(foo: Callable) -> _GracefulCallable:
    """
    A decorator that wraps callable in infinite loop that can be quit gracefully
    :param foo:
    :return:
    """
    return __GracefulInfiniteLoop(foo)


def GracefulThread(thread_class: threading.Thread.__class__):
    """
    A decorator that defines a GracefulThread
    :param thread_class:
    :return:
    """
    graceful_thread_init = _GracefulThread.__init__
    original_init = thread_class.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        graceful_thread_init(self, thread_class.run)
        self.run.hook = self

    thread_class.__init__ = __init__
    thread_class.stop = _GracefulThread.stop
    return thread_class
