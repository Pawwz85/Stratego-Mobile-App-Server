from abc import ABC, abstractmethod

from src.Core.User import UserDto


class IUserRepository(ABC):
    """
    Interface for interacting with the user repository.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def find_user_by_id(self, id: str) -> UserDto | None:
        """
        Finds a user by their unique ID.

        :param id: The ID of the user to find.
        :return: The requested user or None if not found.
        """

    @abstractmethod
    def find_user_by_username(self, username: str) -> UserDto | None:
        """
        Finds a user by their username.

        :param username: The username of the user to find.
        :return: The requested user or None if not found.
        """

    @abstractmethod
    def add_user(self, user: UserDto) -> bool:
        """
        Adds a new user to the repository.

        :param user: The details of the new user.
        :return: True if the user was added successfully, False otherwise.
        """

    @abstractmethod
    def remove_user(self, user: UserDto) -> bool:
        """
        Removes an existing user from the repository.

        :param user: The details of the user to remove.
        :return: True if the user was removed successfully, False otherwise.
        """

    @abstractmethod
    def is_tester(self, user: UserDto) -> bool:
        """
        Checks whether a user has tester privileges.

        :param user: The details of the user to check.
        :return: True if the user is a tester, False otherwise.
        """
