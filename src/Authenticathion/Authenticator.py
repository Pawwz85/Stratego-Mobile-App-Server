import json

from src.Authenticathion.UserDao import UserDao
from src.Core.IUserRepository import IUserRepository
import hashlib

from src.Core.User import UserDto


class Authenticator:

    def __init__(self, config: dict):
        self.user_repository: IUserRepository = UserDao(config)

    def hash_password(self, password: str):
        password_bytes = password.encode('utf-8')
        hash_object = hashlib.sha256(password_bytes)
        return hash_object.hexdigest()

    def authenticate(self, auth: dict) -> UserDto | None:
        try:
            username = auth["username"]
            password = self.hash_password(auth["password"])

            if type(username) is not str or type(password) is not str:
                return None

            result = self.user_repository.find_user_by_username(username)
            if result is None or result.password != password:
                return None
        except KeyError as e:
            print(e)
            return None
        return result


if __name__ == "__main__":
    with open('../../Config/secret_config.properties') as file:
        config = json.load(file)

    print("Password encryption tool")
    password = input("Type password to encrypt")
    auth = Authenticator(config)
    print("Your encrypted password is: ", auth.hash_password(password))
