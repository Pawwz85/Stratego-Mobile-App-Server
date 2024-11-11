from threading import Lock


class SingletonException(BaseException):
    pass


def raise_singleton_exception():
    raise SingletonException


def singleton(cls):
    class Wrapped:
        def __init__(self, *args, **kwargs):
            pass

    Wrapped.__init__ = cls.__init__
    cls.__init__ = raise_singleton_exception
    cls._out_queue_lock = Lock()
    cls._instance = None

    def get_instance(*args, **kwargs):
        with cls._out_queue_lock:
            if cls._instance is None:
                cls._instance = Wrapped(*args, **kwargs)
            return cls._instance

    cls.get_instance = staticmethod(get_instance)
    return cls

