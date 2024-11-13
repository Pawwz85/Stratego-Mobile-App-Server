from Environment.RedisEnvironment import RedisEnvironment

# TODO: figure some way to customise this, like creating a setup script
testing_environment = RedisEnvironment("redis://127.0.0.1:6379")
