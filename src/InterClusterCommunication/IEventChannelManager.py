from abc import ABC, abstractmethod
from collections.abc import Callable


class IPubSub(ABC):

    @abstractmethod
    async def subscribe(self, channel_name: str, callback: Callable):
        pass

    @abstractmethod
    async def unsubscribe(self, channel_name: str):
        pass

    @abstractmethod
    async def publish(self, channel_name: str, msg: str):
        pass

    @abstractmethod
    async def listen(self):
        pass


class IChannelRouting(ABC):
    @abstractmethod
    async def set_routing(self, key: str, channel: str):
        pass

    @abstractmethod
    async def get_routing(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def discard_routing(self, key: str):
        pass


class IRequestQueueClient(ABC):

    @abstractmethod
    async def enqueue_request(self, request: str):
        """
        Add a message to the queue.
        At most 1 worker may consume any given request
        :param request: The message to be added.
        :return: None
        """


class IRequestQueueWorker(ABC):
    @abstractmethod
    async def consume_requests(self, callback: Callable[[str], any]):
        """
        Listen and consume message from queue.

        In this context, consuming mean draining underlying message broker queue in the way, that
        ensures that this worker node is and will be only worker to consume given message.
        :return: None
        """

    @abstractmethod
    def stop_consuming(self):
        """
            Coroutine consume_requests() will be suspended
        """

    @abstractmethod
    def start_consuming(self):
        """
            Coroutine consume_requests() will be reactivated
        """


class IChannelGrouping(ABC):
    @abstractmethod
    async def add_channel_to_group(self, channel: str, group: str) -> str:
        pass

    @abstractmethod
    async def remove_channel_from_group(self, handle: str):
        pass

    @abstractmethod
    async def get_group(self, group: str) -> list[str]:
        pass


class IChannelManager(ABC):

    @abstractmethod
    def get_pub_sub(self) -> IPubSub:
        pass

    @abstractmethod
    def get_group_manager(self) -> IChannelGrouping:
        pass

    @abstractmethod
    def get_routing_manager(self) -> IChannelRouting:
        pass

    @abstractmethod
    def get_request_queue(self) -> IRequestQueueClient:
        pass

    @abstractmethod
    def get_request_queue_worker(self) -> IRequestQueueWorker:
        pass
