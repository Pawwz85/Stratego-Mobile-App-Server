import pep249
import abc


class IDatabaseConnectionFactory(abc.ABC):
    @abc.abstractmethod
    def get_connection(self) -> pep249.Connection:
        raise NotImplementedError

    @staticmethod
    def verify_config(config: dict) -> bool:
        raise NotImplementedError


class IDatabaseConnectionAbstractFactory(abc.ABC):

    @abc.abstractmethod
    def get_connection_factory(self) -> IDatabaseConnectionFactory:
        raise NotImplementedError
