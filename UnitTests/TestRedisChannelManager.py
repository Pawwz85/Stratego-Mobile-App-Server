import asyncio

import fakeredis

from UnitTests.test_ichannel_manager import TestPubSub, TestChannelRouting, TestChannelGrouping
from src.InterClusterCommunication.RedisChannelManager import RedisGroupManager, RedisPubSub, RedisRoutingManager


class RedisPubSubTest(TestPubSub):
    def setUp(self):
        redis = fakeredis.FakeAsyncRedis()
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.consumer = RedisPubSub(redis)
        self.producer = RedisPubSub(redis)


class RedisGroupTest(TestChannelGrouping):
    def setUp(self):
        redis = fakeredis.FakeAsyncRedis()
        self.group_api1 = RedisGroupManager(redis)
        self.group_api2 = RedisGroupManager(redis)


class RedisRoutingTest(TestChannelRouting):
    def setUp(self):
        redis = fakeredis.FakeAsyncRedis()
        self.router1 = RedisRoutingManager(redis)
        self.router2 = RedisRoutingManager(redis)

