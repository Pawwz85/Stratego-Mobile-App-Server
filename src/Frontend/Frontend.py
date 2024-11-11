import json
import os
import signal
import time

import flask
import flask_login
from flask import Flask, request, session
from flask_login import login_user
from flask_socketio import SocketIO, join_room, leave_room
from redis.asyncio import Redis

import login
from src.AsyncioWorkerThread import AsyncioWorkerThread
from src.Authenticathion.Authenticator import Authenticator
from src.Authenticathion.UserDao import UserDao
from src.Core.User import HttpUser
from src.Frontend.IntermediateRequestIDMapper import IntermediateRequestIDMapper
from src.Frontend.TemporalStorageService import TemporalStorageService
from src.Frontend.message_processing import UserResponseBufferer
from src.Frontend.socketio_socket_management import SocketManager
from src.InterClusterCommunication.GameNodeAPICallsBuilder import GameNodeApiRequestFactory
from src.InterClusterCommunication.HandleGameNodeMessage import GameNodeAPIHandler
from src.InterClusterCommunication.RedisChannelManager import RedisChannelManager

app = Flask(__name__)
socketio = SocketIO(app, always_connect=True)
response_bufferer = UserResponseBufferer()
socket_manager = SocketManager()
with open('../../Config/secret_config.properties') as file:
    config = json.load(file)
app.config["SECRET_KEY"] = config["secret_key"]


app_login = login.AppLogin(app, config)
asyncio_worker = AsyncioWorkerThread()
user_service = UserDao(config)
redis = Redis.from_url(config["redis_url"])
channel_manager = RedisChannelManager(redis)

stream_manager = GameNodeAPIHandler(socketio,
                                    IntermediateRequestIDMapper(),
                                    response_bufferer,
                                    channel_manager,
                                    asyncio_worker)

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
    req = GameNodeApiRequestFactory().create_get_room_info_request(room_id)
    user = flask_login.current_user
    user = user.get_dto()

    res = response_bufferer.get_parsed_response(user.username, req.get("message_id"))

    if res is None:
        stream_manager.on_user_request(user, req)
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
        user = flask_login.current_user.get_dto()
        stream_manager.on_user_request_dict(user, req)
        return flask.redirect("/create_room/processing/" + response_id)


@app.route("/create_room/processing/<response_id>")
@login_required
def process_create_room(response_id: str):
    res = response_bufferer.get_parsed_response(session["username"], response_id)
    status = res.get("status", "timed out")
    #print(res)
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
        user = flask_login.current_user.get_dto()
        stream_manager.on_user_request_dict(user, req)

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


@app.route("/register", methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')


@socketio.on("request")
def handle_request_event(ev):
    user = flask_login.current_user.get_dto()
    stream_manager.on_user_request(user, ev)


@socketio.on("connect")
def handle_connect():
    join_room(session["username"])
    print(session["username"] + " has been connected")


@socketio.on("disconnect")
def handle_connect():
    leave_room(session["username"])
    print(session["username"] + " has been disconnected")


async def init_stream():
    pub_sub = channel_manager.get_pub_sub()
    await pub_sub.subscribe(config["frontend_api_channel_name"], stream_manager.HandleGameNodeMessage)
    await  pub_sub.listen()



def start_server():

    temporal_storage_service = TemporalStorageService(response_bufferer, socket_manager)
    temporal_storage_service.start()
    asyncio_worker.add_task(init_stream())
    asyncio_worker.start()

    def stop_services(signum, frame):
        print("stopping...")
        temporal_storage_service.stop()
        asyncio_worker.stop()
        print("Killing main process in 3s")
        time.sleep(3)
        os.kill(os.getpid(), signal.SIGINT)

    signal.signal(signal.SIGINT, stop_services)
    signal.signal(signal.SIGTERM, stop_services)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

    temporal_storage_service.join()


if __name__ == "__main__":
    start_server()
