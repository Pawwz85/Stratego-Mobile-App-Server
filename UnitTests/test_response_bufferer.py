import time
import unittest
from src.Server.message_processing import ResponseBufferer, UserResponseBufferer


class TestResponseBufferer(unittest.TestCase):
    def setUp(self):
        self._buffer = ResponseBufferer(3)

    def tearDown(self):
        del self._buffer

    def test_get_not_existing_response(self):
        res = self._buffer.get_response("test")
        self.assertIsNone(res)

    def test_get_response(self):
        self._buffer.add_response("test", "desired outcome")
        self._buffer.add_response("test2", "idk")
        res = self._buffer.get_response("test")
        self.assertEqual(res, "desired outcome")

    def test_response_time_out(self):
        self._buffer.add_response("test", "some outdated thing", 0.1)
        time.sleep(0.2)
        self._buffer.discard_old_entries()
        res = self._buffer.get_response("test")
        self.assertIsNone(res)

    def test_get_refreshes_msg(self):
        self._buffer.add_response("test", "desired outcome", 0.1, True)
        time.sleep(0.05)
        self._buffer.discard_old_entries()
        self._buffer.get_response("test")
        time.sleep(0.07)
        self._buffer.discard_old_entries()
        res = self._buffer.get_response("test")
        self.assertEqual(res, "desired outcome")

    def test_turn_off_refresh_on_touch(self):
        self._buffer.add_response("test", "undesired outcome", 0.1, False)
        time.sleep(0.05)
        self._buffer.discard_old_entries()
        self._buffer.get_response("test")
        time.sleep(0.07)
        self._buffer.discard_old_entries()
        res = self._buffer.get_response("test")
        self.assertIsNone(res)

    def test_default_timed_out(self):
        self._buffer.add_response("test", "desired outcome", refresh_on_touch=False)
        time.sleep(2.9)
        self._buffer.discard_old_entries()
        self.assertEqual("desired outcome", self._buffer.get_response("test"))
        time.sleep(0.2)
        self._buffer.discard_old_entries()
        self.assertIsNone(self._buffer.get_response("test"))


class TestUserResponseBufferer(unittest.TestCase):
    def setUp(self):
        self._buffer = UserResponseBufferer()

    def tearDown(self):
        del self._buffer

    def test_get_not_existing_response(self):
        res = self._buffer.get_response("SYSTEM", "test")
        self.assertIsNone(res)

    def test_get_response(self):
        self._buffer.add_response("SYSTEM", "test", "desired outcome")
        self._buffer.add_response("SYSTEM", "test2", "idk")
        res = self._buffer.get_response("SYSTEM", "test")
        self.assertEqual(res, "desired outcome")

    def test_response_time_out(self):
        self._buffer.add_response("SYSTEM", "test", "some outdated thing", 0.1)
        time.sleep(0.2)
        self._buffer.discard_old_entries()
        res = self._buffer.get_response("SYSTEM", "test")
        self.assertIsNone(res)

    def test_get_refreshes_msg(self):
        self._buffer.add_response("SYSTEM", "test", "desired outcome", 0.1, True)
        time.sleep(0.05)
        self._buffer.discard_old_entries()
        self._buffer.get_response("SYSTEM", "test")
        time.sleep(0.07)
        self._buffer.discard_old_entries()
        res = self._buffer.get_response("SYSTEM", "test")
        self.assertEqual(res, "desired outcome")

    def test_turn_off_refresh_on_touch(self):
        self._buffer.add_response("SYSTEM", "test", "undesired outcome", 0.1, False)
        time.sleep(0.05)
        self._buffer.discard_old_entries()
        self._buffer.get_response("SYSTEM", "test")
        time.sleep(0.07)
        self._buffer.discard_old_entries()
        res = self._buffer.get_response("SYSTEM", "test")
        self.assertIsNone(res)

    def test_default_timed_out(self):
        self._buffer.add_response("SYSTEM", "test", "desired outcome", refresh_on_touch=False)
        time.sleep(9.9)
        self._buffer.discard_old_entries()
        self.assertEqual("desired outcome", self._buffer.get_response("SYSTEM", "test"))
        time.sleep(0.2)
        self._buffer.discard_old_entries()
        self.assertIsNone(self._buffer.get_response("SYSTEM", "test"))


if __name__ == '__main__':
    unittest.main()
