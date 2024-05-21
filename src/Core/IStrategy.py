from abc import ABC, abstractmethod
from typing import Callable


class IStrategy(ABC):
    def __init__(self, preconditions: Callable[[any], bool], strategy: Callable):
        self.__times_applied = 0
        self.preconditions = preconditions
        self.strategy = strategy

    def __call__(self, *args, **kwargs):
        if self.preconditions(*args, **kwargs):
            self.__times_applied = self.__times_applied + 1
            self.strategy(*args, **kwargs)

    def get_times_applied(self):
        return self.__times_applied


class IStrategyRepository(ABC):
    @abstractmethod
    def add_strategy(self, strategy: IStrategy):
        pass

    @abstractmethod
    def remove_strategy(self, strategy: IStrategy):
        pass


class IStrategyPicker(ABC):
    def __init__(self, strategy_repository: IStrategyRepository, default_strategy: IStrategy):
        self.repository = strategy_repository
        self.default_strategy = default_strategy

    @abstractmethod
    def pick_strategy(self, event: any) -> IStrategy:
        pass


def print_strategy(message: str) -> IStrategy:
    return IStrategy(lambda x: True, lambda x: print(message, x))
