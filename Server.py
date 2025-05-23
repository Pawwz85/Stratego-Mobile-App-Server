import os
import signal
import time
from collections.abc import Callable

import flask
import flask_login
from flask import Flask, request, session
from flask_login import login_user
from flask_socketio import SocketIO, join_room, leave_room
from redis.asyncio import Redis

import src.Server.login as login
from src.AsyncioWorkerThread import AsyncioWorkerThread
from src.Authenticathion.Authenticator import Authenticator
from src.Authenticathion.UserDao import UserDao
from src.Core.User import HttpUser, UserIdentity
from src.Server.IntermediateRequestIDMapper import IntermediateRequestIDMapper
from src.Server.RoomBrowser import RoomBrowser, GlobalRoomListCache, RoomInfo
from src.Server.TemporalStorageService import TemporalStorageService
from src.Server.message_processing import UserResponseBufferer
from src.Server.socket_manager import SocketManager, SocketioUserSocket
from src.Server.socketio_socket_management import send_event_to_user
from src.Server.websocket_service import WebsocketService
from src.Core.InterClusterCommunication.GameNodeAPICallsBuilder import GameNodeApiRequestFactory
from src.Core.InterClusterCommunication.HandleGameNodeMessage import GameNodeAPIHandler
from src.Core.InterClusterCommunication.RedisChannelManager import RedisChannelManager
from src.RegistrationController import RegistrationController
from src.Server.ServerCLI import parse_config_from_cli
from src.DatabaseConnection.ConcreteDatabaseConnectionFactory import ConcreteDatabaseConnectionFactory

config = parse_config_from_cli()
app = Flask(__name__)
socketio = SocketIO(app, always_connect=True)
send_event = lambda username, e: send_event_to_user(socketio, username=username, e=e)

response_bufferer = UserResponseBufferer()
socket_manager = SocketManager()

app.config["SECRET_KEY"] = config["secret_key"]

database_connection_abstract_factory = ConcreteDatabaseConnectionFactory(config)
user_service = UserDao(config, database_connection_abstract_factory.get_connection_factory())

app_login = login.AppLogin(app, user_service)
asyncio_worker = AsyncioWorkerThread()
registration_controller = RegistrationController(response_bufferer, user_service, config)
redis = Redis.from_url(config["redis_url"])
channel_manager = RedisChannelManager(redis)

game_node_api_handler = GameNodeAPIHandler(
    IntermediateRequestIDMapper(),
    response_bufferer,
    channel_manager,
    asyncio_worker,
    socket_manager.emit_event_by_signature)

websocket_service = WebsocketService(config, game_node_api_handler, socket_manager, asyncio_worker)

global_room_list_cache = GlobalRoomListCache(game_node_api_handler, channel_manager)
room_browser = RoomBrowser(global_room_list_cache)

authenticator = Authenticator(user_service)


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
            login_user(HttpUser.from_user_identity(user))
            flask.flash("Logged in successfully.")
            session["username"] = user.username
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
    req = GameNodeApiRequestFactory().create_get_room_info_request(room_id)
    user = flask_login.current_user
    user = user.get_user_identity()

    res = response_bufferer.get_parsed_response(user.username, req.get("message_id"))

    if res is None:
        game_node_api_handler.send_request(send_event, req, user)
        res = {"status": "processing"}

    status = res.get("status", "timed_out")

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
        control_params = request.form.deepcopy()
        req = GameNodeApiRequestFactory().create_create_room_request(control_params)
        response_id = req.get("message_id")
        user = flask_login.current_user.get_user_identity()
        game_node_api_handler.send_request(send_event, req, user)
        return flask.redirect("/create_room/processing/" + response_id)


@app.route("/create_room/processing/<response_id>")
@login_required
def process_create_room(response_id: str):
    res = response_bufferer.get_parsed_response(session["username"], response_id)
    status = res.get("status", "timed out")
    # print(res)
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
        control_params = request.form.deepcopy()
        req = GameNodeApiRequestFactory().create_join_room_request(control_params, room_id)
        response_id = req.get("message_id")
        user = flask_login.current_user.get_user_identity()
        game_node_api_handler.send_request(send_event, req, user)

        return flask.redirect("/join_room/processing/" + room_id + "/" + response_id)
    else:
        return flask.redirect("/error")


@app.route("/join_room/processing/<room_id>/<response_id>")
@login_required
def process_join_room(room_id: str, response_id: str):
    res = response_bufferer.get_parsed_response(session["username"], response_id)
    status = res.get("status", "timed_out")

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


@app.route("/browse_rooms", methods=['GET', 'POST'])
@login_required
def browse_room():
    _filter = lambda x: True
    hide_password_protected_rooms_value = ""
    selected_game_phase = {
        "all": "selected",
        "awaiting": "",
        "setup": "",
        "gameplay": "",
        "finished": ""
    }
    if request.method == "POST":
        print(request.form.deepcopy())
        selected_game_phase["all"] = ""
        phase = request.form.get("game_phase_filter", "all")
        selected_game_phase[phase] = "selected"
        if request.form.get("hide_password_protected_rooms") == "on":
            print(request.form.get("hide_password_protected_rooms"))
            _filter: Callable[[RoomInfo], bool] = lambda info: not info.password_required
            hide_password_protected_rooms_value = "checked"

        if phase != "all":
            old_filter = _filter
            _filter = lambda info: old_filter(info) and info.game_phase == phase

    rooms = room_browser.browse(filter_by=_filter)
    print(rooms)
    return flask.render_template("room_browser.html", rooms=rooms,
                                 hide_password_protected_rooms_value=hide_password_protected_rooms_value,
                                 selected_game_phase=selected_game_phase)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return flask.render_template('register.html')
    if request.method == "POST":
        errors = {}

        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if username is None or username == "":
            errors["err_username"] = "Username can not be empty"

        if password is None or password == "":
            errors["err_password"] = "Password can't be empty"

        if email is None or email == "":
            errors["err_email"] = "Email can not be none"

        if authenticator.user_repository.find_user_by_username(username) is not None:
            errors["err_username"] = "Username is already taken"

        if len(errors) == 0:
            reg_id = registration_controller.create_registration_id(username, password, email)
            registration_controller.send_mail(username, email, reg_id)
            return flask.render_template('check_mail.html')
        else:
            values = {"val_" + field: request.form.get(field, "") for field in ["username", "password", "email"]}
            return flask.render_template('register.html', **errors, **values)


@app.route("/register/<registration_id>")
def confirm_registration(registration_id: str):
    user: UserIdentity | None
    error: str | None
    user, error = registration_controller.confirm_registration(registration_id)

    if user is not None:
        login_user(HttpUser.from_user_identity(user))
        flask.flash("Logged in successfully.")
        session["username"] = user.username
        return flask.redirect("/")

    return flask.render_template("register_link_expired.html", error=error)


@socketio.on("request")
def handle_request_event(ev):
    user = flask_login.current_user.get_user_identity()
    game_node_api_handler.on_user_request(user, ev, send_event)


@socketio.on("connect")
def handle_connect():
    join_room(session["username"])
    socket = SocketioUserSocket(session["username"], socketio)
    session["socket"] = socket
    socket_manager.register_entry(socket)
    print(session["username"] + " has been connected")


@socketio.on("disconnect")
def handle_connect():
    leave_room(session["username"])
    session.get("socket").close()
    print(session["username"] + " has been disconnected")


async def init_stream():
    pub_sub = channel_manager.get_pub_sub()
    await pub_sub.subscribe(config["frontend_api_channel_name"], game_node_api_handler.handle_game_node_message)
    await pub_sub.listen()


def start_server():
    temporal_storage_service = TemporalStorageService(response_bufferer, socket_manager)
    temporal_storage_service.start()
    websocket_service.run()
    asyncio_worker.add_task(init_stream())
    asyncio_worker.add_task(global_room_list_cache.sync())
    asyncio_worker.start()

    def stop_services(_, __):
        print("stopping...")
        temporal_storage_service.stop()
        asyncio_worker.stop()
        websocket_service.stop_flag.set()
        print("Killing main process in 3s")
        time.sleep(3)
        os.kill(os.getpid(), signal.SIGINT)

    signal.signal(signal.SIGINT, stop_services)
    signal.signal(signal.SIGTERM, stop_services)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

    temporal_storage_service.join()


if __name__ == "__main__":
    start_server()
