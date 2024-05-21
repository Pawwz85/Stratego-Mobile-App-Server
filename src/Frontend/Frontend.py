import json
from flask import Flask, session
from flask_socketio import SocketIO, join_room, close_room

from src.Authenticathion.Authenticator import Authenticator
from src.Core.IStrategy import print_strategy, IStrategy
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategyRepository, \
    MessageStrategyPicker, BackendMessageListenerService
from redis import Redis

from src.FrontendBackendBridge.WebsocketBackendCaller import WebsocketBackendCaller
from src.message_processing import ResponseBufferer

app = Flask(__name__)
socketio = SocketIO(app)
redis = Redis()


def handle_incoming_event(event: dict):
    signature: str | list[str] = event["signature"]
    if type(signature) is not str | list:
        raise RuntimeError("Empty signature")

    room_id: str = event["room_id"]
    if room_id is not None:
        event.pop("signature")

        if type(signature) is str:
            socketio.send(event, json=True, to="user_"+signature)
        else:
            for user in signature:
                socketio.send(event, json=True, to="user_" + user)


backend_response_repository = BackendResponseStrategyRepository()
backend_message_strategy_picker = MessageStrategyPicker(
    backend_response_repository,
    IStrategy(lambda x: True, handle_incoming_event),
    print_strategy("unexpected_response: "),
    print_strategy("can not resolve strategy for this: ")
)

with open('../../Config/secret_config.properties') as file:
    config = json.load(file)
authenticator = Authenticator(config)
response_bufferer = ResponseBufferer()
websocketBackendCaller = WebsocketBackendCaller(backend_response_repository,
                                                redis,
                                                config,
                                                socketio,
                                                response_bufferer)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@socketio.on("connect")
def connection_handler(auth):
    user_dto = authenticator.authenticate(auth)
    if user_dto is None:
        return False
    else:
        session["user_dto"] = user_dto
        join_room("user_" + user_dto.username)


@socketio.on("disconnect")
def disconnection_handler():
    user_dto = session.get("user_dto")
    if user_dto is not None:
        close_room("user_" + user_dto.username)
    session.pop("user_dto")

    # TODO: remove user from all rooms on worker threads


@socketio.on("json")
def json_payload_handler(js):
    message_id = js.get("message_id")
    if message_id is None:
        response = {
            "type": "invalid_message",
            "error": "Untagged or wrongly formatted message",
            "original_message": json.dumps(js)}
        socketio.send(response, json=True)
        return

    if response_bufferer.check_for_response(message_id):
        try:
            response = json.loads(response_bufferer.get_response(message_id))
            socketio.send(response, json=True)
            # TODO: add thread to clean bufferer
        except Exception as e:
            print(e)
    websocketBackendCaller.call(js, session.get("user_dto"), 10, lambda: print("Backend not responding"))


if __name__ == "__main__":
    backend_listener_service = BackendMessageListenerService(redis, config, backend_message_strategy_picker)
    backend_listener_service.start()
    socketio.run(app)
