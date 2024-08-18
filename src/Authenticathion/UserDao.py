from __future__ import annotations
from src.Core.IUserRepository import IUserRepository
from src.Core.User import UserDto
import psycopg2


class UserDao(IUserRepository):
    def __init__(self, config: dict):
        self.connection_factory = lambda: psycopg2.connect(
            dbname=config["db_name"],
            host=config["db_host"],
            password=config["db_password"],
            port=config["db_port"],
            user=config["db_user"]
        )
        self.config = config
        super().__init__()

    def find_user_by_id(self, id: str) -> UserDto | None:
        connection: psycopg2._psycopg.connection | None = None
        cursor: psycopg2._psycopg.cursor | None = None
        try:
            connection = self.connection_factory()
            cursor = connection.cursor()
            sql = "SELECT username, password, id FROM t_users WHERE id = %s;"
            data = (id,)
            cursor.execute(sql, data)
            result_tuple = cursor.fetchone()
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        result = UserDto(*result_tuple) if result_tuple is not None else None
        return result

    def find_user_by_username(self, username: str) -> UserDto | None:
        connection: psycopg2._psycopg.connection | None = None
        cursor: psycopg2._psycopg.cursor | None = None
        try:
            connection = self.connection_factory()
            cursor = connection.cursor()
            sql = "SELECT username, password, id FROM t_users WHERE username = %s;"
            data = (username,)
            cursor.execute(sql, data)
            result_tuple = cursor.fetchone()
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        result = UserDto(*result_tuple) if result_tuple is not None else None
        return result

    def add_user(self, user: UserDto) -> bool:
        connection: psycopg2._psycopg.connection | None = None
        cursor: psycopg2._psycopg.cursor | None = None
        try:
            connection = self.connection_factory()
            cursor = connection.cursor()
            sql = "INSERT INTO t_users (username, password, id, is_tester) VALUES(%s, %s, %s, FALSE);"
            data = (user.username, user.password, user.user_id)
            cursor.execute(sql, data)
            result = True
        except psycopg2.errors.Error:
            result = False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        return result

    def remove_user(self, user: UserDto) -> bool:
        connection: psycopg2._psycopg.connection | None = None
        cursor: psycopg2._psycopg.cursor | None = None
        try:
            connection = self.connection_factory()
            cursor = connection.cursor()
            sql = "DELETE FROM t_users WHERE id = %s;"
            data = (user.user_id,)
            cursor.execute(sql, data)
            result = True
        except psycopg2.errors.Error:
            result = False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        return result

    def is_tester(self, user: UserDto) -> bool:
        connection: psycopg2._psycopg.connection | None = None
        cursor: psycopg2._psycopg.cursor | None = None
        try:
            connection = self.connection_factory()
            cursor = connection.cursor()
            sql = "SELECT is_tester FROM t_users WHERE id = %s;"
            data = (user.user_id,)
            cursor.execute(sql, data)
            result = cursor.fetchone()
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        return True if result else False
