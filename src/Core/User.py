from src.Events.Events import EventLogicalEndpoint, Eventmanager


class User:
    def __init__(self, username: str, password: str, user_id: int,
                 event_man: Eventmanager, signature: str | None = None):
        self.username = username
        self.id = user_id
        self.password = password
        self.room_count = 0
        self.session: EventLogicalEndpoint =\
            EventLogicalEndpoint(event_man, username if signature is None else signature)


class UserDto:
    def __init__(self, username: str, password: str, user_id: int):
        self.username = username
        self.password = password
        self.user_id = user_id
