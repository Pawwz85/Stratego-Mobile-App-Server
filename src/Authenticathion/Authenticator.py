import json

from src.Authenticathion.UserDao import UserDao
from src.Core.IUserRepository import IUserRepository
import hashlib

from src.Core.User import UserIdentity


class Authenticator:

    def __init__(self, config: dict):
        self.user_repository: IUserRepository = UserDao(config)

    @staticmethod
    def hash_password(password: str, salt: str):
        salted = password + salt
        password_bytes = salted.encode('utf-8')
        hash_object = hashlib.sha256(password_bytes)
        return hash_object.hexdigest()

    def authenticate(self, auth: dict) -> UserIdentity | None:
        try:
            username = auth["username"]
            password = auth["password"]

            if type(username) is not str or type(password) is not str:
                return None

            result = self.user_repository.find_user_by_username(username)
            print(result)

            password_hash = self.hash_password(password, result.salt if result.salt else "") if result else None

            if result is None or result.password != password_hash:
                return None
        except KeyError as e:
            print(e)
            return None
        return result.to_user_identity() if result else None


if __name__ == "__main__":
    with open('../../Config/secret_config.properties') as file:
        config = json.load(file)

    print("Password encryption tool")
    password = input("Type password to encrypt")
    salt = input("Type salt to strengthen the encryption")
    auth = Authenticator(config)
    print("Your encrypted password is: ", auth.hash_password(password, salt))
