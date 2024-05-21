from abc import ABC, abstractmethod
from typing import Callable


class IStrategy(ABC):
    """
    An abstract class representing a strategy.
    """
    def __init__(self, preconditions: Callable[[any], bool], strategy: Callable):
        """
         An abstract class representing a strategy.
        :param preconditions: A function that checks if strategy could be used on given data
        :param strategy: A procedure to perform on given data.
        """
        self.__times_applied = 0  # This fields counts how many times strategy was successfully applied
        self.preconditions = preconditions
        self.strategy = strategy

    def __call__(self, *args, **kwargs):
        if self.preconditions(*args, **kwargs):
            self.__times_applied = self.__times_applied + 1
            self.strategy(*args, **kwargs)

    def get_times_applied(self):
        """
        A method returning how many times a data handling procedure of strategy was called
        :return:
        """
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
    """
    Prints received data after given message, used as a placeholder
    :param message: Message to print before data
    :return:
    """
    return IStrategy(lambda x: True, lambda x: print(message, x))
