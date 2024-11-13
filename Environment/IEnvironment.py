from abc import ABC, abstractmethod


class IEnvironment(ABC):

    @abstractmethod
    def setUp(self):
        """
        Sets up an environment
        """

    @abstractmethod
    def cleanUp(self):
        """
        Cleans up an environment
        """

    @abstractmethod
    def create_game_node(self, config: dict) -> int:
        """
        Spawns a new game node in current configuration
        :param config: A configuration for a new game node
        :return: a handle of created node, can be used to destroy this node
        """

    @abstractmethod
    def destroy_game_node(self, node_handle: int):
        """
        Destroys a specified node
        :param node_handle:
        :return:
        """

    @abstractmethod
    def get_broker_service_url(self) -> str:
        pass

    def __enter__(self):
        self.setUp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanUp()
