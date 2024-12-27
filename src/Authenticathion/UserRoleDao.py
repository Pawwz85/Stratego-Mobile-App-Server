import pep249
import psycopg2
from src.Core.IUserRoleRepository import IUserRoleRepository, UserRole, PrivilegeManagementError
from src.DatabaseConnection.IConnectionFactory import IDatabaseConnectionFactory


class UserRoleDao(IUserRoleRepository):

    def __init__(self, config: dict, connection_factory: IDatabaseConnectionFactory):
        self.connection_factory = connection_factory
        self.config = config
        super().__init__()

    def revoke_role(self, user_id: int, role: UserRole):
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        error_occurred = False
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()
            sql = "DELETE FROM t_user_user_roles WHERE user_id = %s AND role_id = %s;"
            cursor.execute(sql, [str(user_id), str(role.id)])
            connection.commit()
        except psycopg2.errors.Error:
            error_occurred = True
        finally:
            cursor.close()
            connection.close()

        if error_occurred:
            raise PrivilegeManagementError("Failed to revoke role")

    def grant_role(self, user_id: int, role: UserRole):
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        error_occurred = False
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()
            sql = "INSERT INTO t_user_user_roles VALUES(%s, %s);"
            cursor.execute(sql, [str(user_id), str(role.id)])
            connection.commit()
        except psycopg2.errors.Error:
            error_occurred = True
        finally:
            cursor.close()
            connection.close()

        if error_occurred:
            raise PrivilegeManagementError("Failed to grant role")

    def get_roles(self, user_id) -> set[UserRole] | None:
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        result: set[UserRole] | None = None
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()

            sql = ("SELECT (role_id, name) FROM (t_user_user_roles JOIN t_user_roles ON role_id = id)  WHERE user_id = "
                   "%s;")
            cursor.execute(sql, [user_id])
            roles = cursor.fetchall()
            result = {UserRole(*role) for role in roles}
        except BaseException:
            error_occurred = True
        finally:
            cursor.close()
            connection.close()
        return result
