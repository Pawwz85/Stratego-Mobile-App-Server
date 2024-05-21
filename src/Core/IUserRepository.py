from abc import ABC, abstractmethod

from src.Core.User import UserDto


class IUserRepository(ABC):
    
    def __init__(self):
        super().__init__()

    @abstractmethod
    def find_user_by_id(self, id: str) -> UserDto | None:
        pass

    @abstractmethod
    def find_user_by_username(self, username: str) -> UserDto | None:
        pass

    @abstractmethod
    def add_user(self, user: UserDto) -> bool:
        pass

    @abstractmethod
    def remove_user(self, user: UserDto) -> bool:
        pass

