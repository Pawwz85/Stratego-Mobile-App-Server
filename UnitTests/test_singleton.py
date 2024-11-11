from __future__ import annotations

from src.Core.singleton import singleton


@singleton
class ExampleSingleton:
    def __init__(self):
        self.some_variable = 7

    @staticmethod
    def get_instance() -> ExampleSingleton:
        pass


@singleton
class ExampleSingleton2:
    def __init__(self, some_var):
        self.some_var = some_var

    @staticmethod
    def get_instance(some_var) -> ExampleSingleton2:
        pass


