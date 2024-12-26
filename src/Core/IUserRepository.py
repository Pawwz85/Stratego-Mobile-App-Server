import dataclasses
from abc import ABC, abstractmethod

from src.Core.IUserRoleRepository import UserRole
from src.Core.User import UserIdentity


@dataclasses.dataclass
class UserDatabaseObject:
    username: str
    password: str
    user_id: int
    salt: str
    email: str | None

    def to_user_identity(self):
        return UserIdentity(self.username, self.user_id)


class IUserRepository(ABC):
    """
    Interface for interacting with the user repository.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def find_user_by_id(self, id: str) -> UserDatabaseObject | None:
        """
        Finds a user by their unique ID.

        :param id: The ID of the user to find.
        :return: The requested user or None if not found.
        """

    @abstractmethod
    def find_user_by_username(self, username: str) -> UserDatabaseObject | None:
        """
        Finds a user by their username.

        :param username: The username of the user to find.
        :return: The requested user or None if not found.
        """

    @abstractmethod
    def add_user(self, user: UserDatabaseObject) -> bool:
        """
        Adds a new user to the repository.

        :param user: The details of the new user.
        :return: True if the user was added successfully, False otherwise.
        """

    @abstractmethod
    def remove_user(self, user: UserDatabaseObject) -> bool:
        """
        Removes an existing user from the repository.

        :param user: The details of the user to remove.
        :return: True if the user was removed successfully, False otherwise.
        """

    @abstractmethod
    def get_users_by_role(self, role: UserRole) -> list[UserDatabaseObject]:
        """
        Retrieves a list of users possessing given role.

        :param role: Role
        """