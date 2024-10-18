import json
import os
import signal
import time

import flask
import flask_login

import login
from flask import Flask, request, session
from flask_login import login_user
from flask_socketio import SocketIO, join_room, leave_room

from src.Authenticathion.Authenticator import Authenticator
from src.Authenticathion.UserDao import UserDao
from src.Core.IStrategy import print_strategy, IStrategy
from src.Core.User import HttpUser
from src.Frontend.TemporalStorageService import TemporalStorageService
from src.Frontend.socketio_socket_management import SocketManager, send_event_to_socketio_clients
from src.Frontend.websocket_service import WebsocketService
from src.FrontendBackendBridge.GameNodeAPICallsBuilder import GameNodeApiRequestFactory
from src.FrontendBackendBridge.GameNodeQuery import SynchronousGameNodeQuery
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategyRepository, \
    MessageStrategyPicker, BackendMessageListenerService
from redis import Redis
from src.Frontend.message_processing import UserResponseBufferer
from src.FrontendBackendBridge.SocketioBackendCaller import SocketioBackendCaller
from src.FrontendBackendBridge.WebsocketBackendCaller import WebsocketBackendCaller

app = Flask(__name__)
socketio = SocketIO(app, always_connect=True)
response_bufferer = UserResponseBufferer()
socket_manager = SocketManager()
backend_response_repository = BackendResponseStrategyRepository()
with open('../../Config/secret_config.properties') as file:
    config = json.load(file)
app.config["SECRET_KEY"] = config["secret_key"]

app_login = login.AppLogin(app, config)
user_service = UserDao(config)
redis = Redis.from_url(config["redis_url"])
web_socket_service = WebsocketService("/websocket", response_bufferer, redis, config, backend_response_repository)
socketio_backend_caller = SocketioBackendCaller(backend_response_repository, redis, config, socketio)
backend_message_strategy_picker = MessageStrategyPicker(
    backend_response_repository,
    IStrategy(lambda x: True, lambda d: (web_socket_service.send_event_to_users(d),
                                         send_event_to_socketio_clients(socketio, d))),
    print_strategy("unexpected_response: "),
    print_strategy("can not resolve strategy for this: ")
)
authenticator = Authenticator(config)


def login_required(route):
    def wrapper(*args, **kwargs):
        user = flask_login.current_user
        if not user.is_authenticated:
            return flask.redirect("/login")
        return route(*args, **kwargs)

    wrapper.__name__ = route.__name__
    return wrapper


@app.route('/', methods=['GET'])
@login_required
def index():
    return flask.render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = authenticator.authenticate(request.form)
        if user is not None:
            login_user(HttpUser.from_dto(user))
            flask.flash("Logged in successfully.")
            session["username"] = user.username
            session["is_tester"] = authenticator.user_repository.is_tester(user)
            return flask.redirect("/")

    session.get("username")
    return flask.render_template('login.html')


@app.route("/board", methods=['GET'])
@login_required
def test_board():
    return flask.render_template('board.html')


@app.route("/room_search", methods=['GET'])
@login_required
def play():
    return flask.render_template('room_search.html')


@app.route("/get_room_info", methods=["POST"])
@login_required
def search_for_room():
    return flask.redirect("/get_room_info/" + request.form.get("room_id", "blank"))


@app.route("/get_room_info/<room_id>")
@login_required
def get_room_info(room_id: str):
    game_node_query = SynchronousGameNodeQuery(response_bufferer, backend_response_repository, redis, config)
    req = GameNodeApiRequestFactory().create_get_room_info_request(room_id)

    user = flask_login.current_user
    user = user.get_dto()

    res = game_node_query.call(req, user, 10.0)
    status = res.get("status", "timed_out")
    print(req, res)
    metadata: dict | None = res.get("metadata", None)
    if metadata:
        metadata["room_id"] = room_id

    possible_responses = {
        "processing": flask.render_template("loading_screen.html"),
        "timed out": flask.render_template("room_not_found.html", room_id=room_id),
        "failure": flask.render_template("room_not_found.html", room_id=room_id),
        "success": flask.render_template("room_preview.html", room_metadata=metadata),
        "error": flask.redirect("/error")
    }
    return possible_responses.get(status)


@app.route("/create_room", methods=['GET', 'POST'])
@login_required
def create_room():
    if request.method == "GET":
        return flask.render_template("create_room.html")
    if request.method == "POST":
        game_node_query = SynchronousGameNodeQuery(response_bufferer, backend_response_repository, redis, config)
        control_params = request.form.deepcopy()
        req = GameNodeApiRequestFactory().create_create_room_request(control_params)
        response_id = req.get("message_id")
        user = flask_login.current_user
        game_node_query.call(req, user.get_dto(), 10.0)
        return flask.redirect("/create_room/processing/" + response_id)


@app.route("/create_room/processing/<response_id>")
@login_required
def process_create_room(response_id: str):
    user = flask_login.current_user
    res = json.loads(response_bufferer.get_response(session["username"], response_id))
    status = res.get("status", "timed_out")
    possible_responses = {
        "processing": flask.render_template("loading_screen.html"),
        "timed out": flask.redirect("/create_room"),
        "failure": flask.redirect("/create_room"),
        "success": flask.redirect("/play/room/" + res.get("room_id", "error")),
        "error": None
    }
    return possible_responses.get(status)


@app.route("/join_room/<room_id>", methods=['POST', 'GET'])
@login_required
def join_room_route(room_id: str):
    if request.method == "GET":
        return flask.redirect("/room_search")
    elif request.method == "POST":
        game_node_query = SynchronousGameNodeQuery(response_bufferer, backend_response_repository, redis, config)
        control_params = request.form.deepcopy()
        req = GameNodeApiRequestFactory().create_join_room_request(control_params, room_id)
        response_id = req.get("message_id")
        user = flask_login.current_user
        game_node_query.call(req, user.get_dto(), 10.0)
        return flask.redirect("/join_room/processing/" + room_id + "/" + response_id)
    else:
        return flask.redirect("/error")


@app.route("/join_room/processing/<room_id>/<response_id>")
@login_required
def process_join_room(room_id: str, response_id: str):
    user = flask_login.current_user
    res = json.loads(response_bufferer.get_response(session["username"], response_id))
    status = res.get("status", "timed_out")
    print(res, status)
    possible_responses = {
        "processing": flask.render_template("loading_screen.html"),
        "timed out": flask.redirect("/room_search"),
        "failure": flask.redirect("/room_search") if res.get("cause") != "You are already in this room"
        else flask.redirect("/play/room/" + room_id),
        "success": flask.redirect("/play/room/" + room_id),
        "error": None
    }
    return possible_responses.get(status)


@app.route("/play/room/<room_id>")
@login_required
def server_game_client(room_id: str | int):
    boot_info = {
        "username": session["username"],
        "room_id": room_id
    }
    return flask.render_template("board.html", boot_info=boot_info)


@app.route("/register", methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')


@socketio.on("request")
def handle_request_event(ev):
    user = flask_login.current_user.get_dto()
    socketio_backend_caller.call(ev, user, 10, lambda: None)


@socketio.on("connect")
def handle_connect():
    d = join_room(session["username"])
    print(session["username"] + " has been connected")


@socketio.on("disconnect")
def handle_connect():
    leave_room(session["username"])
    print(session["username"] + " has been disconnected")


def start_server():
    backend_listener_service = BackendMessageListenerService(redis, config, backend_message_strategy_picker)
    backend_listener_service.start()
    temporal_storage_service = TemporalStorageService(response_bufferer, socket_manager)
    temporal_storage_service.start()
    web_socket_service.start()

    def stop_services(signum, frame):
        print("stopping...")
        temporal_storage_service.stop()
        backend_listener_service.stop()
        web_socket_service.stop_flag.set()
        print("Killing main process in 3s")
        time.sleep(3)
        os.kill(os.getpid(), signal.SIGINT)

    signal.signal(signal.SIGINT, stop_services)
    signal.signal(signal.SIGTERM, stop_services)
    # app.run(host='127.0.0.1', port=5000)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

    web_socket_service.join()
    temporal_storage_service.join()
    backend_listener_service.join()


if __name__ == "__main__":
    start_server()
