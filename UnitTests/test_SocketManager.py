import time
import unittest
from unittest.mock import Mock
from src.Server.socket_manager import SocketManager, IUserSocket, SocketType


class UserSocketMock(IUserSocket):
    def emit(self, event: dict):
        return self.mock(event)

    def __init__(self, type_: SocketType, username: str):
        super().__init__(type_, username)
        self.mock = Mock()

    def _close(self):
        pass


class SocketManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.socket_manager = SocketManager()

    def tearDown(self):
        del self.socket_manager

    def test_register_user(self):
        mocked_user = UserSocketMock(SocketType.WEBSOCKET, "tester")
        self.socket_manager.register_entry(mocked_user)
        self.assertIs(mocked_user, self.socket_manager.get_socket("tester"))

    def test_remove_old_entries(self):
        mocked_user = UserSocketMock(SocketType.WEBSOCKET, "tester")
        self.socket_manager.remember_time = 1
        self.socket_manager.register_entry(mocked_user)
        self.socket_manager.remove_old_entries()
        self.assertIs(mocked_user, self.socket_manager.get_socket("tester"))
        time.sleep(1)
        self.socket_manager.remove_old_entries()
        self.assertIsNone(self.socket_manager.get_socket("tester"))

    def test_emit_by_signature(self):
        mocked_user = UserSocketMock(SocketType.WEBSOCKET, "tester")
        self.socket_manager.register_entry(mocked_user)
        self.socket_manager.emit_event_by_signature({"signature": ["tester"]})
        self.assertTrue(mocked_user.mock.called)
        print(mocked_user.mock.call_args)

    def test_emit_multiple_sockets_for_single_user(self):
        sockets = [UserSocketMock(SocketType.WEBSOCKET, "tester") for _ in range(10)]
        for s in sockets:
            self.socket_manager.register_entry(s)
        self.socket_manager.emit_event_by_signature({"signature": ["tester"]})
        for s in sockets:
            self.assertTrue(s.mock.called)


if __name__ == '__main__':
    unittest.main()
