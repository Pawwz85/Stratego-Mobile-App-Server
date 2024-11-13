

class GameNodeConfigBuilder:
    """
        Run time Game Node config builder; used in some unit tests
    """
    def __init__(self):
        self.config = {
            "redis_url": "redis://127.0.0.1:6379",
            "unique_game_node_channel": "example_name",
            "frontend_node_cluster_broadcast_chanel": "frontend_channel",
            "game_node_protocol_version": "1.0",
            "max_room_count": 250,
        }

    def redis_url(self, value=None):
        if value is not None:
            self.config["redis_url"] = value
        return self

    def unique_game_node_channel(self, value=None):
        if value is not None:
            self.config["unique_game_node_channel"] = value
        return self

    def frontend_node_cluster_broadcast_chanel(self, value=None):
        if value is not None:
            self.config["frontend_node_cluster_broadcast_chanel"] = value
        return self

    def game_node_protocol_version(self, value=None):
        if value is not None:
            self.config["game_node_protocol_version"] = value
        return self

    def max_room_count(self, value=None):
        if value is not None:
            self.config["max_room_count"] = value
        return self

    def build(self):
        return self.config
