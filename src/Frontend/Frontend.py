import json
from flask import Flask
from flask_socketio import SocketIO

from src.Authenticathion.Authenticator import Authenticator
from src.Core.IStrategy import print_strategy, IStrategy
from src.Frontend.websocket_service import WebsocketService
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategyRepository, \
    MessageStrategyPicker, BackendMessageListenerService
from redis import Redis

from src.message_processing import ResponseBufferer, ResponseBuffererService

app = Flask(__name__)
socketio = SocketIO(app)
redis = Redis()
response_bufferer = ResponseBufferer()
backend_response_repository = BackendResponseStrategyRepository()
with open('../../Config/secret_config.properties') as file:
    config = json.load(file)

web_socket_service = WebsocketService("/websocket", response_bufferer, redis, config, backend_response_repository)


backend_message_strategy_picker = MessageStrategyPicker(
    backend_response_repository,
    IStrategy(lambda x: True, lambda d: web_socket_service.send_event_to_users(d)),
    print_strategy("unexpected_response: "),
    print_strategy("can not resolve strategy for this: ")
)
authenticator = Authenticator(config)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    backend_listener_service = BackendMessageListenerService(redis, config, backend_message_strategy_picker)
    backend_listener_service.start()
    ResponseBuffererService(response_bufferer).start()
    web_socket_service.start()
    socketio.run(app, allow_unsafe_werkzeug=True, host='0.0.0.0')
