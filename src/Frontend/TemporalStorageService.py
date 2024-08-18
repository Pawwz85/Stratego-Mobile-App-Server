import time
from threading import Thread

from src import GracefulThreads
from src.Frontend.message_processing import UserResponseBufferer
from src.Frontend.socketio_socket_management import SocketManager


@GracefulThreads.GracefulThread
class TemporalStorageService(Thread):
    def __init__(self, bufferer: UserResponseBufferer, socket_manager: SocketManager):
        self.bufferer = bufferer
        self.socketManager: socket_manager = socket_manager
        super().__init__()

    @GracefulThreads.loop_forever_gracefully
    def run(self):
        time.sleep(10)
        self.bufferer.discard_old_entries()
        self.socketManager.remove_old_entries()
