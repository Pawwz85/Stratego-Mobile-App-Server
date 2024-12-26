import json
import random
import uuid
import smtplib
import email
from src.Authenticathion.Authenticator import Authenticator
from src.Core.IUserRepository import IUserRepository, UserDatabaseObject
from string import ascii_letters, digits

from src.Core.User import UserIdentity
from src.Frontend.message_processing import UserResponseBufferer


class RegistrationController:
    def __init__(self, store: UserResponseBufferer, repository: IUserRepository, config: dict):
        self._store = store
        self._repo = repository
        self._config = config
        self._connection = smtplib.SMTP(config["smtp_host"], config["smtp_port"])

    def send_mail(self, username: str, email_address: str, registration_id: str):
        msg = email.message.EmailMessage()
        msg["From"] = "SYSTEM@" + self._config["domain_name"]
        msg["To"] = email_address
        msg["Subject"] = "Your email verification link"
        link = "".join(["www.", self._config["domain_name"], "/register/", registration_id])
        msg.set_content(f"Hello {username}! Your registration link is {link} The link expires in 5 minutes.")
        self._connection.send_message(msg)

    def create_registration_id(self, username: str, password: str, email: str) -> str:
        salt = "".join(random.choice(ascii_letters + digits) for _ in range(10))
        req_data = {
            "username": username,
            "password": Authenticator.hash_password(password, salt),
            "email": email,
            "salt": salt,
            "user_id": -1
        }
        data = json.dumps(req_data)
        registration_id: str = uuid.uuid4().hex

        self._store.add_response("SYSTEM", registration_id, data, 300, False)
        return registration_id

    def confirm_registration(self, registration_id: str) -> tuple[UserIdentity | None, str | None]:

        response = self._store.get_response("SYSTEM", registration_id)

        if response in [None, "expired"]:
            return None, "Link expired"

        try:
            user_data = json.loads(response)
            user = UserDatabaseObject(**user_data)
        except json.JSONDecodeError:
            return None, "Incorrect data"
        except KeyError:
            return None, "Request is missing fields"

        if user.username == "SYSTEM":
            return None, "'SYSTEM' is a prohibited username"

        result = self._repo.add_user(user)

        self._store.add_response("SYSTEM", registration_id, "expired")

        if result is None:
            return None, "User creation failed"

        # fetch user from database, so we will get an id generated by database
        user = self._repo.find_user_by_username(user.username)

        if user is None:
            return None, "Could not load an user id from database"

        return user.to_user_identity(), None