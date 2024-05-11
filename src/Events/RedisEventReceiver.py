import json
from typing import Callable

from redis import Redis

from src.Events.Events import IEventReceiver, Eventmanager


class RedisPubSubEventReceiver(IEventReceiver):
    def receive(self, message: str):
        self.redis.publish(self.channel_name, message)
        event_body = json.loads(message)
        event_id = event_body["event_id"]
        self.event_manager.confirm_delivery(event_id)

    def __init__(self, on_disconnect: Callable, event_man: Eventmanager,
                 redis: Redis, channel_name):
        self.redis = redis
        self.channel_name = channel_name
        self.event_manager = event_man
        super().__init__(on_disconnect)
