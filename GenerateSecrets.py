import argparse
import pathlib
import string
import random

from src.ToolsAndUtilitty.ConfigManager.ConfigFileSchema import ConfigFileSchema, ConfigFile, entry_schema, JSONConfigController

REDIS_URL = 'redis://127.0.0.1:6379'
REQUEST_QUEUE_NAME = 'request_queue'
BACKEND_API_CHANNEL_NAME = 'request_channel'
FRONTEND_API_CHANNEL_NAME = 'frontend_channel'
POSTGRES_DB_TYPE = 'Postgres'
DOMAIN_NAME = 'localhost:5000'
SECRET_KEY_LENGTH = 32
SMTP_PORT = 25
SMTP_HOST = '127.0.0.1'


def generate_secret_key():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(SECRET_KEY_LENGTH))


def generate_db_user():
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    return f'stratego_{username}'


schema = ConfigFileSchema()
# register defaults,
schema.add_schema("redis", entry_schema(REDIS_URL))
schema.add_schema("request_queue", entry_schema(REQUEST_QUEUE_NAME))
schema.add_schema("backend_api_channel", entry_schema(BACKEND_API_CHANNEL_NAME))
schema.add_schema("frontend_api_channel", entry_schema(FRONTEND_API_CHANNEL_NAME))
schema.add_schema("db_type", entry_schema(POSTGRES_DB_TYPE))
schema.add_schema("domain_name", entry_schema(DOMAIN_NAME))
schema.add_schema("secret_key", entry_schema(generate_secret_key))
schema.add_schema("db_user", entry_schema(generate_db_user))
schema.add_schema("smtp_host", entry_schema(SMTP_HOST))
schema.add_schema("smtp_port", entry_schema(SMTP_PORT))


class SecretConfigController(JSONConfigController):
    def set_db(self, args):
        query = {
               "db_type": args.type,
               "db_name": args.name,
               "db_host": args.host,
               "dp_port": args.port
        }
        self._bulk_value_set({k: v for k, v in query.items() if v is not None})

    def set_db_credentials(self, args):
        query = {
            "db_user": args.user,
            "db_password": args.password
        }
        self._bulk_value_set({k: v for k, v in query.items() if v is not None})


if __name__ == "__main__":
    config = ConfigFile(pathlib.Path('Config/secret_config.properties'), schema)
    controller = SecretConfigController(config)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Set subcommand
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("key", help="The key to set in the configuration.")
    set_parser.add_argument("value", help="The value to set in the configuration.")
    set_parser.set_defaults(func=controller.set_variable)
    # DB subcommand
    db = subparsers.add_parser("db")
    # Set single key for db properties
    db.add_argument("--type", choices=["Postgres", "SQLite"], type=str, help="The database type to set.")
    db.add_argument("--name", type=str, help="The name of the database to set.")
    db.add_argument("--host", type=str, help="The host of the database to set.")
    db.add_argument("--port", type=int, help="The port number of the database to set.")
    db.set_defaults(func=controller.set_db)
    # DB Credentials subcommand
    db_cred = subparsers.add_parser("db-cred")
    db_cred.add_argument("--user", type=str, help="The username of the database to set.")
    db_cred.add_argument("--password", type=str, help="The password of the database to set.")
    db_cred.set_defaults(func=controller.set_db_credentials)

    touch = subparsers.add_parser("touch")
    touch.set_defaults(func=controller.touch)

    args = parser.parse_args()

    func = args.func
    args.func(args)