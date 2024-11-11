import asyncio
import uuid
from typing import Callable

from redis.asyncio import Redis

from src.InterClusterCommunication.IEventChannelManager import IChannelManager, IChannelRouting, IChannelGrouping, \
    IPubSub, IRequestQueueClient, IRequestQueueWorker


class RedisPubSub(IPubSub):
    def __init__(self, redis: Redis):
        self._pub_sub = redis.pubsub()
        self._redis = redis

    @staticmethod
    def _extract_msg_data(msg):
        m = msg['data'].decode("utf-8")
        return m

    async def subscribe(self, channel_name: str, callback: Callable):
        kwargs = {
            channel_name: lambda msg: callback(self._extract_msg_data(msg))
        }
        await self._pub_sub.subscribe(**kwargs)
        print("subscribed to ", f'"{channel_name}"')

    async def unsubscribe(self, channel_name: str):
        await self._pub_sub.unsubscribe(channel_name)

    async def publish(self, channel_name: str, msg: str):
        print("published to", f'"{channel_name}"')
        await self._redis.publish(channel_name, msg)

    async def listen(self):
        print("Listening")
        await self._pub_sub.run()


class RedisRoutingManager(IChannelRouting):

    def __init__(self, redis: Redis):
        self._redis = redis

    @staticmethod
    def encode(key: str):
        print(f"encoding key: {key}")
        return "route:" + key

    async def set_routing(self, key: str, channel: str):
        await self._redis.set(self.encode(key), channel)
        test = await self.get_routing(key)
        print(test)

    async def get_routing(self, key: str) -> str | None:
        result = await self._redis.get(self.encode(key))
        return result.decode("utf-8") if result is not None else None

    async def discard_routing(self, key: str):
        await self._redis.delete(self.encode(key))


class RedisGroupManager(IChannelGrouping):
    def __init__(self, redis: Redis):
        self._redis = redis

    def _get_handle(self, channel: str, group: str) -> str:
        # TODO: generate random handle and store it
        return channel

    def _get_channel_name_by_handle(self, handle: str) -> str:
        return handle

    async def _save_group_of_channel(self, channel: str, group: str):
        await self._redis.set("gr:" + channel, group)

    async def _get_group_of_channel(self, channel: str):
        result = await self._redis.get("gr:" + channel)
        return result.decode("utf-8") if result is not None else None

    async def add_channel_to_group(self, channel: str, group: str) -> str:
        await self._redis.lpush(group, channel)
        handle = self._get_handle(channel, group)
        return handle

    async def remove_channel_from_group(self, handle: str):
        channel = self._get_channel_name_by_handle(handle)
        group: str = await self._get_group_of_channel(channel)
        if group is not None:
            await self._redis.lrem(group,  1, channel)

    async def get_group(self, group: str) -> list[str]:
        result = await self._redis.lrange(group, 0, -1)
        return [s.decode("utf-8") for s in result]


class RedisRequestQueue(IRequestQueueClient, IRequestQueueWorker):
    def __init__(self, redis: Redis, redis_lock: str, queue_name: str):
        self._redis = redis
        self._redis_queue_lock = redis_lock
        self._id = uuid.uuid4().hex
        self._queue_name = queue_name
        self._consume: Callable[[str], any] = lambda x: None
        self._active = True

    async def enqueue_request(self, request: str):
        print("enqueued " + request)
        while True:
            await self._redis.setnx(self._redis_queue_lock, self._id)
            lock_value = await self._redis.get(self._redis_queue_lock)
            lock_value = str(lock_value, "utf-8")

            if lock_value == self._id:
                await self._redis.lpush(self._queue_name, request)
                await self._redis.delete(self._redis_queue_lock)
                break

    async def _try_consume(self):
        print("try consume")
        await self._redis.setnx(self._redis_queue_lock, self._id)
        lock_value = await self._redis.get(self._redis_queue_lock)
        lock_value = str(lock_value, "utf-8")
        print(lock_value, self._id, lock_value == self._id)
        if lock_value == self._id:
            req = await self._redis.rpop(self._queue_name, 1)
            await self._redis.delete(self._redis_queue_lock)
            if req is not None:

                [self._consume(x) for x in req] if type(req) is list else self._consume(req)

    async def consume_requests(self, callback: Callable[[str], any]):
        self._consume = callback
        while True:
            await asyncio.sleep(3)
            if self._active:
                await self._try_consume()

    def stop_consuming(self):
        self._active = True

    def start_consuming(self):
        self._active = False


class RedisChannelManager(IChannelManager):
    def __init__(self, redis: Redis):
        self._redis = redis
        self._pub_sub = RedisPubSub(redis)
        self._router = RedisRoutingManager(redis)
        self._group_manager = RedisGroupManager(redis)

        queue_lock = "request_queue_lock"
        queue_name = "request_queue"
        self._request_queue_manager = RedisRequestQueue(redis, queue_lock, queue_name)

    def get_pub_sub(self) -> IPubSub:
        return self._pub_sub

    def get_group_manager(self) -> IChannelGrouping:
        return self._group_manager

    def get_routing_manager(self) -> IChannelRouting:
        return self._router

    def get_request_queue(self) -> IRequestQueueClient:
        return self._request_queue_manager

    def get_request_queue_worker(self) -> IRequestQueueWorker:
        return self._request_queue_manager
