import json
import os
import signal
import time

import flask

import login
from flask import Flask, request
from flask_login import current_user, login_user

from src.Authenticathion.Authenticator import Authenticator
from src.Authenticathion.UserDao import UserDao
from src.Core.IStrategy import print_strategy, IStrategy
from src.Core.User import HttpUser
from src.Frontend.websocket_service import WebsocketService
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategyRepository, \
    MessageStrategyPicker, BackendMessageListenerService
from redis import Redis
from src.message_processing import ResponseBufferer, ResponseBuffererService

app = Flask(__name__)
response_bufferer = ResponseBufferer()
backend_response_repository = BackendResponseStrategyRepository()
with open('../../Config/secret_config.properties') as file:
    config = json.load(file)
app.config["SECRET_KEY"] = config["secret_key"]

app_login = login.AppLogin(app, config)
user_service = UserDao(config)
redis = Redis.from_url(config["redis_url"])
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = authenticator.authenticate(request.form)
        if user is not None:
            login_user(HttpUser.from_dto(user))
            flask.flash("Logged in successfully.")
            return flask.redirect("/")

    return flask.render_template('login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')



if __name__ == "__main__":
    backend_listener_service = BackendMessageListenerService(redis, config, backend_message_strategy_picker)
    backend_listener_service.start()
    response_bufferer_service = ResponseBuffererService(response_bufferer)
    response_bufferer_service.start()
    web_socket_service.start()

    def stop_services(signum, frame):
        print("stopping...")
        response_bufferer_service.stop()
        backend_listener_service.stop()
        web_socket_service.stop_flag.set()
        print("Killing main process in 3s")
        time.sleep(3)
        os.kill(os.getpid(), signal.SIGINT)

    signal.signal(signal.SIGINT, stop_services)
    signal.signal(signal.SIGTERM, stop_services)
    app.run(host='0.0.0.0', port=5000)
