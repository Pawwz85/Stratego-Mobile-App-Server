import json
from typing import Callable
from threading import Lock, Thread

from redis import Redis

from src import GracefulThreads
from src.Core.IStrategy import IStrategy, IStrategyRepository, IStrategyPicker


class BackendResponseStrategy(IStrategy):
    def __init__(self, request_id: str, strategy: Callable):
        self.request_id = request_id
        super().__init__(lambda d: d.get("response_id", "") == request_id, strategy)

    def __hash__(self):
        return self.request_id.__hash__()


class BackendResponseStrategyRepository(IStrategyRepository):
    def remove_strategy(self, strategy: BackendResponseStrategy):
        try:
            with self.lock:
                self.strategies.pop(strategy.request_id)
        except KeyError as e:
            pass

    def add_strategy(self, strategy: BackendResponseStrategy):
        with self.lock:
            self.strategies[strategy.request_id] = strategy

    def __init__(self):
        self.lock = Lock()
        self.strategies: dict[str, BackendResponseStrategy] = dict()


class BackendResponseStrategyPicker(IStrategyPicker):
    def __init__(self, strategy_repository: BackendResponseStrategyRepository, default_strategy: IStrategy):
        super().__init__(strategy_repository, default_strategy)

    def pick_strategy(self, event: dict) -> IStrategy:
        repo: BackendResponseStrategyRepository | IStrategyRepository = self.repository
        try:
            with repo.lock:
                result = repo.strategies.get(event.get("response_id", ""), self.default_strategy)
            return result
        except Exception as e:
            print(e)
            return self.default_strategy


class MessageStrategyPicker(IStrategyPicker):
    def pick_strategy(self, event: any) -> IStrategy:
        with self.lock:
            print(event)
            if event.get("event_id") is not None:
                print("event")
                return self.event_handler
            elif event.get("response_id") is not None:
                return self.__response_strategy_picker.pick_strategy(event)
            else:
                return self.default_strategy

    def __init__(self, strategy_repository: BackendResponseStrategyRepository,
                 event_handler: IStrategy,
                 unexpected_response_handler: IStrategy,
                 default_strategy: IStrategy):
        self.event_handler = event_handler
        self.lock = Lock()
        self.__response_strategy_picker = BackendResponseStrategyPicker(strategy_repository,
                                                                        unexpected_response_handler)
        super().__init__(strategy_repository, default_strategy)


@GracefulThreads.GracefulThread
class BackendMessageListenerService(Thread):
    def __init__(self, redis: Redis, config: dict, strategy_picker: MessageStrategyPicker):
        self.pub_sub = redis.pubsub()
        self.pub_sub.subscribe(config["frontend_api_channel_name"])
        self.strategy_picker = strategy_picker
        super().__init__()

    @GracefulThreads.loop_forever_gracefully
    def run(self):
        for message in self.pub_sub.listen():
            if message["type"] == "message":
                msg = json.loads(message["data"])
                print(msg)
                strategy = self.strategy_picker.pick_strategy(msg)
                strategy(msg)
