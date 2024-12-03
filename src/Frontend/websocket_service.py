import asyncio
import json
import threading
from threading import Thread, Lock
from redis import Redis
from websockets import serve, ServerProtocol
from websockets.asyncio.server import Server, ServerConnection

from src.AsyncioWorkerThread import AsyncioWorkerThread
from src.Authenticathion.Authenticator import Authenticator
from src.Core.User import UserDto
from src.Frontend.socket_manager import WebsocketUserSocket, SocketManager
from src.Frontend.websocket_api import WebsocketStream, WebsocketInfo
from src.InterClusterCommunication.HandleGameNodeMessage import GameNodeAPIHandler


class WebsocketService:

    def __init__(self, config: dict, api_handler: GameNodeAPIHandler,
                 socket_manager: SocketManager, worker: AsyncioWorkerThread):
        self.stop_flag = threading.Event()
        self.lock = Lock()
        self.auth = Authenticator(config)
        self.worker = worker
        self._stream = WebsocketStream(api_handler, self.auth, socket_manager)

    async def __websocket_endpoint(self, websocket: ServerConnection):
        socket = WebsocketUserSocket("", websocket, self.worker)
        socket_info = WebsocketInfo(socket, None)

        async for msg in websocket:
            socket.touch()
            print(str(msg))
            self._stream.handle_request(str(msg), socket_info)

    async def __service_main(self):
        async with serve(self.__websocket_endpoint,
                         host="localhost",
                         port=5001) as server:
            future = asyncio.Future()
            asyncio.ensure_future(self.__check_stop_flag(server, future))
            await future

    async def __check_stop_flag(self, server: Server, future: asyncio.Future):
        while not self.stop_flag.is_set():
            await asyncio.sleep(1)
        server.close()
        future.cancel()

    def run(self):
        try:
            print("websocket run")
            self.worker.add_task(self.__service_main())
        except asyncio.exceptions.CancelledError:
            print("Stopped websocket service")
