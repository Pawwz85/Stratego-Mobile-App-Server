import dataclasses
from enum import Enum
from abc import ABC, abstractmethod


@dataclasses.dataclass
class UserRole:
    id: int
    name: str


class PrivilegeManagementError(BaseException):
    pass


class IUserRoleRepository(ABC):

    @abstractmethod
    def revoke_role(self, user_id: int, role: UserRole):
        """
            Revoke provided role from the user having provided id
            Raises PrivilegeManagementError on failure.
        """

    @abstractmethod
    def grant_role(self, user_id: int, role: UserRole):
        """
            Grant provided role to the user having provided id.
            Raises PrivilegeManagementError on failure.
        """

    @abstractmethod
    def get_roles(self, user_id) -> set[UserRole] | None:
        """
            Get roles that given user has.
            Returns None if user is not found
        """
