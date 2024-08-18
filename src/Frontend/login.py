from flask import Flask
from flask_login import LoginManager

from src.Core.User import HttpUser
from src.Authenticathion.UserDao import UserDao


class AppLogin:
    def __init__(self, app: Flask, config: dict):
        self.login_manager = LoginManager()
        self.login_manager.init_app(app)
        self.user_dao = UserDao(config)

        @self.login_manager.user_loader
        def load_user(user_id: str):
            user_dto = self.user_dao.find_user_by_id(user_id)
            if user_dto:
                return HttpUser.from_dto(user_dto)

