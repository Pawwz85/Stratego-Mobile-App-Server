from __future__ import annotations


from src.Core.IUserRepository import IUserRepository, UserDatabaseObject

import pep249
from src.Core.IUserRoleRepository import UserRole
from src.DatabaseConnection.IConnectionFactory import IDatabaseConnectionFactory


class UserDao(IUserRepository):
    def __init__(self, config: dict, connection_factory: IDatabaseConnectionFactory):
        self.connection_factory: IDatabaseConnectionFactory = connection_factory
        self.config = config
        super().__init__()

    def find_user_by_id(self, id: str) -> UserDatabaseObject | None:
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()
            sql = "SELECT username, password, id, salt, email FROM t_users WHERE id = %s;"
            data = (id,)
            cursor.execute(sql, data)
            result_tuple = cursor.fetchone()
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        result = UserDatabaseObject(*result_tuple) if result_tuple is not None else None
        return result

    def find_user_by_username(self, username: str) -> UserDatabaseObject | None:
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()
            sql = "SELECT username, password, id, salt, email FROM t_users WHERE username = %s;"
            data = (username,)
            cursor.execute(sql, data)
            result_tuple = cursor.fetchone()
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        result = UserDatabaseObject(*result_tuple) if result_tuple is not None else None
        return result

    def add_user(self, user: UserDatabaseObject) -> bool:
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()

            sql = "select max(id) from t_users"
            cursor.execute(sql)
            id_ = cursor.fetchone()
            id_ = (id_[0] + 1) if id_ else 1

            sql = "INSERT INTO t_users (username, password, salt, email) VALUES(%s, %s,  %s, %s);"
            data = (user.username, user.password, user.salt, user.email)
            cursor.execute(sql, data)

            connection.commit()
            result = True
        except BaseException:
            result = False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        return result

    def remove_user(self, user: UserDatabaseObject) -> bool:
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()
            sql = "DELETE FROM t_users WHERE id = %s;"
            data = (user.user_id,)
            cursor.execute(sql, data)
            connection.commit()
            result = True
        except BaseException:
            result = False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        return result

    def get_users_by_role(self, role: UserRole) -> list[UserDatabaseObject]:
        connection: pep249.Connection | None = None
        cursor: pep249.Cursor | None = None
        try:
            connection = self.connection_factory.get_connection()
            cursor = connection.cursor()
            sql = ("SELECT username, password, id, salt, email FROM (t_users JOIN t_user_user_roles ON id = user_id) "
                   "WHERE username = %s;")
            data = (role.id,)
            cursor.execute(sql, data)
            query_result = cursor.fetchall()
            result = [UserDatabaseObject(*u) for u in query_result]
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        return result
