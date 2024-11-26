from Environment.RedisEnvironment import RedisEnvironment, RedisServerBootManager
from pathlib import Path

# TODO: add config files that would allow to configure booting local redis-server
testing_environment = RedisEnvironment("redis://127.0.0.1:6379",
                                       RedisServerBootManager(Path("Environment/scripts/win_start_redis_server_on_wsl"
                                                                   ".bat").absolute(), "redis://127.0.0.1:6379"))

staging_environment = RedisEnvironment("redis://127.0.0.1:6379")

