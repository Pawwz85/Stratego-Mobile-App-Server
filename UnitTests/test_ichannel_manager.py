import asyncio
import unittest
from abc import ABC
from unittest.mock import Mock

from src.InterClusterCommunication.IEventChannelManager import (IChannelGrouping, IChannelRouting, IPubSub)


# noinspection PyUnreachableCode
class TestPubSub(unittest.TestCase):

    def setUp(self):
        self.skipTest("This is just ABC, override this method in derived classes")
        self.consumer: IPubSub = IPubSub()
        self.producer: IPubSub = IPubSub()

    def tearDown(self):
        del self.consumer, self.producer

    def test_IPubSub(self):
        loop = asyncio.get_event_loop()
        callback = Mock()

        async def kill_loop(loop_to_stop: asyncio.AbstractEventLoop):
            await asyncio.sleep(10)
            loop_to_stop.stop()

        async def pub():
            await asyncio.sleep(1)
            await self.producer.publish("test_channel", "test")

        async def sub():
            await self.consumer.subscribe("test_channel", callback)
            await self.consumer.listen()

        loop.create_task(kill_loop(loop))
        loop.create_task(pub())
        loop.create_task(sub())
        loop.run_forever()
        callback.assert_called_with("test")

    def test_unsubscribe(self):
        loop = asyncio.get_event_loop()
        callback = Mock()

        async def kill_loop(loop_to_stop: asyncio.AbstractEventLoop):
            await asyncio.sleep(10)
            loop_to_stop.stop()

        async def pub():
            await asyncio.sleep(1)
            await self.producer.publish("test_channel", "test")

        async def sub():
            await self.consumer.subscribe("test_channel", callback)
            await self.consumer.unsubscribe("test_channel")

        loop.create_task(kill_loop(loop))
        loop.create_task(pub())
        loop.create_task(sub())
        callback.assert_not_called()


# noinspection PyUnreachableCode
class TestChannelRouting(ABC, unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.skipTest("This is just ABC, override this method in derived classes")
        self.router1: IChannelRouting = IChannelRouting()
        self.router2: IChannelRouting = IChannelRouting()

    def tearDown(self):
        del self.router1, self.router2

    async def test_get_routing(self):
        await self.router1.set_routing("key", "value")
        res = await self.router2.get_routing("key")
        self.assertEqual(res, "value")

    async def test_discard_routing(self):
        await self.router1.set_routing("key", "value")
        await self.router2.discard_routing("key")
        res = await self.router1.get_routing("key")
        self.assertEqual(res, None)


# noinspection PyUnreachableCode
class TestChannelGrouping(ABC, unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.skipTest("This is just ABC, override this method in derived classes")
        self.group_api1: IChannelGrouping = IChannelGrouping()
        self.group_api2: IChannelGrouping = IChannelGrouping()

    def tearDown(self):
        del self.group_api1, self.group_api2

    async def test_get_routing(self):
        await self.group_api1.add_channel_to_group("ch", "group")
        res = await self.group_api2.get_group("group")
        self.assertIn("ch", res)

    async def test_discard_routing(self):
        handle = await self.group_api1.add_channel_to_group("ch", "value")
        await self.group_api1.remove_channel_from_group(handle)
        res = await self.group_api2.get_group("group")
        self.assertNotIn("ch", res)


_skip_abstract_base_class = False

if __name__ == '__main__':
    unittest.main()
