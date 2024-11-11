from redis.asyncio import Redis

from src.GameNode.GameNode import GameNode
from src.GameNode.ConfigLoader import ConfigLoaderStrategy, JsonConfigLoaderFactory
import argparse
from src.InterClusterCommunication.RedisChannelManager import RedisChannelManager


def main(args):
    if args.json_file is not None:
        conf_load_strategy = ConfigLoaderStrategy.LoadFromCustomJsonFile
        args_ = ()
        kwargs = {"file": args.json_file}
        factory = JsonConfigLoaderFactory()
    elif args.json_string is not None:
        conf_load_strategy = ConfigLoaderStrategy.LoadFromJsonString
        args_ = ()
        kwargs = {"json_string": args.json_string}
        print(kwargs)
        factory = JsonConfigLoaderFactory()
    else:
        conf_load_strategy = ConfigLoaderStrategy.LoadFromDefaultJsonFile
        args_ = ()
        kwargs = {}
        factory = JsonConfigLoaderFactory()

    config = factory.build_config(conf_load_strategy, *args_, **kwargs)
    redis = Redis.from_url(config["redis_url"])
    channel_manager = RedisChannelManager(redis)
    system = GameNode(config, channel_manager)
    system.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    parser_config = subparsers.add_parser("config", help="Configure a game node")
    parser_config.add_argument("--json-file", help="Specify a JSON file containing the configuration")
    parser_config.add_argument("--json-string", help="Specify a JSON string containing the configuration")
    args = parser_config.parse_args()
    main(args)