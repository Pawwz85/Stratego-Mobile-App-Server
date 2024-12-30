import argparse
import pathlib
import string
import random

from src.ToolsAndUtilitty.ConfigManager.ConfigFileSchema import ConfigFileSchema, ConfigFile, entry_schema, JSONConfigController

REDIS_URL = 'redis://127.0.0.1:6379'
FRONTEND_API_CHANNEL_NAME = 'frontend_channel'
PROTOCOL_VERSION = "1.0"
MAX_ROOM_COUNT = 250
ENVIRONMENT = "deployment"


def generate_unique_node_channel() -> str:
    return "game_node" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))


schema = ConfigFileSchema()
schema.add_schema("redis_url", entry_schema(REDIS_URL))
schema.add_schema("unique_game_node_channel", entry_schema(generate_unique_node_channel))
schema.add_schema("frontend_node_cluster_broadcast_chanel", entry_schema(FRONTEND_API_CHANNEL_NAME))
schema.add_schema("game_node_protocol_version", entry_schema(PROTOCOL_VERSION))
schema.add_schema("max_room_count", entry_schema(MAX_ROOM_COUNT))
schema.add_schema("enable_privileged_testing_mode", entry_schema(False))
schema.add_schema("environment", entry_schema(ENVIRONMENT))


class GameNodeConfigController(JSONConfigController):
    pass


if __name__ == "__main__":
    cnf = ConfigFile(pathlib.Path("Config/game_node_config.properties"), schema)
    controller = GameNodeConfigController(cnf)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Set subcommand
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("key", help="The key to set in the configuration.")
    set_parser.add_argument("value", help="The value to set in the configuration.")
    set_parser.set_defaults(func=controller.set_variable)

    # touch subcommand
    touch = subparsers.add_parser("touch")
    touch.set_defaults(func=controller.touch)

    args = parser.parse_args()

    func = args.func
    args.func(args)
