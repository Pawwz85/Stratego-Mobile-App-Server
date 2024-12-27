import enum
import sqlite3

import pep249
import psycopg2

from src.DatabaseConnection.IConnectionFactory import IDatabaseConnectionAbstractFactory, IDatabaseConnectionFactory


class SupportedDatabases(enum.Enum):
    Postgres = "Postgres"
    SQLite = "SQLite"


class _PostgresConnectionFactory(IDatabaseConnectionFactory):
    def get_connection(self):
        return psycopg2.connect(dbname=self._config["db_name"],
                                host=self._config["db_host"],
                                password=self._config["db_password"],
                                port=self._config["db_port"],
                                user=self._config["db_user"])

    @staticmethod
    def verify_config(config: dict) -> bool:
        keys_ = {"db_name", "db_host", "db_password", "dp_port", "db_user"}
        return keys_.issubset(config.keys())

    def __init__(self, config: dict):
        self._config = config


class _SQLiteConnectionFactory(IDatabaseConnectionFactory):
    def get_connection(self):
        return sqlite3.connect(database=self._config["db_name"])

    @staticmethod
    def verify_config(config: dict) -> bool:
        keys_ = {"db_name"}
        return keys_.issubset(config.keys())

    def __init__(self, config: dict):
        self._config = config


class ConcreteDatabaseConnectionFactory(IDatabaseConnectionAbstractFactory):

    def __init__(self, config: dict):
        self._factory: IDatabaseConnectionFactory = _SQLiteConnectionFactory(config)
        self._config = config
        self._factories = {
            "SQLite": _SQLiteConnectionFactory,
            "Postgres": _PostgresConnectionFactory
        }
        self._factory = self._factories.get(config.get("db_type"), _SQLiteConnectionFactory)(config)

    def set_factory(self, fac: IDatabaseConnectionFactory):
        self._factory = fac

    def set_factory_by_type(self, db_type_: SupportedDatabases):
        self._factory = self._factories[db_type_.value](self._config)

    def get_connection_factory(self) -> IDatabaseConnectionFactory:
        return self._factory
