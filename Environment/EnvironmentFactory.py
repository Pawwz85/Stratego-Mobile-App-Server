from __future__ import annotations
from Environment.RedisEnvironment import RedisEnvironment, RedisServerBootManager
from pathlib import Path

from src.Core.singleton import singleton


# TODO: add config files that would allow to configure booting local redis-server

@singleton
class EnvironmentFactory:

    def __init__(self):
        self._testing_env = RedisEnvironment("redis://127.0.0.1:6379",
                                             RedisServerBootManager.get_instance(
                                                 Path("Environment/scripts/win_start_redis_server_on_wsl"
                                                      ".bat").absolute(), "redis://127.0.0.1:6379"))
        self._staging_env = RedisEnvironment("redis://127.0.0.1:6379")

    def get_testing_env(self):
        return self._testing_env

    def get_staging_env(self):
        return self._staging_env

    @staticmethod
    def get_instance(*args, **kwargs) -> EnvironmentFactory:
        pass
