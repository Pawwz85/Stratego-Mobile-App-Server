from __future__ import annotations
from Environment.RedisEnvironment import RedisEnvironment, RedisServerBootManager
from pathlib import Path

from src.Core.singleton import singleton


# TODO: add config files that would allow to configure booting local redis-server

@singleton
class EnvironmentFactory:

    def __init__(self):
        pass

    def get_testing_env(self):
        return RedisEnvironment("redis://127.0.0.1:6379",
                         RedisServerBootManager.get_instance(
                             Path("Environment/scripts/win_start_redis_server_on_wsl.bat")
                             .absolute(), "redis://127.0.0.1:6379"))

    def get_staging_env(self):
        return RedisEnvironment("redis://127.0.0.1:6379")

    def create_environment(self, config: dict):
        env = config.get("environment")

        if env == "test":
            return self.get_testing_env()
        elif env == "staging":
            return self.get_staging_env()
        elif env == "deployment":
            return RedisEnvironment(config.get("redis_url", "redis://127.0.0.1:6379"))
        return self.get_testing_env()

    @staticmethod
    def get_instance(*args, **kwargs) -> EnvironmentFactory:
        pass
