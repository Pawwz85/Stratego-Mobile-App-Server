from flask import Flask
from flask_login import LoginManager

from src.Core.IUserRepository import IUserRepository
from src.Core.User import HttpUser
from src.Authenticathion.UserDao import UserDao


class AppLogin:
    def __init__(self, app: Flask, user_service: IUserRepository):
        self.login_manager = LoginManager()
        self.login_manager.init_app(app)
        self.user_dao = user_service

        @self.login_manager.user_loader
        def load_user(user_id: str):
            user = self.user_dao.find_user_by_id(user_id)
            if user:
                return HttpUser.from_user_identity(user.to_user_identity())

