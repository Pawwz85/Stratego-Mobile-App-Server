from threading import Lock


class SingletonException(BaseException):
    pass


def raise_singleton_exception():
    raise SingletonException


def singleton(cls):

    wrapped = type(cls.__name__ + "_instance", cls.__bases__, dict(cls.__dict__))
    wrapped.__init__ = cls.__init__
    
    cls.__init__ = raise_singleton_exception
    cls._out_queue_lock = Lock()
    cls._instance = None

    def get_instance(*args, **kwargs):
        print(f"getting instanceof {cls}, args: {args}, kwargs: {kwargs}")
        with cls._out_queue_lock:
            if cls._instance is None:
                cls._instance = wrapped(*args, **kwargs)
                print(cls, cls._instance)
            return cls._instance

    cls.get_instance = staticmethod(get_instance)
    return cls

