from src.Events import EventLogicalEndpoint, Eventmanager


class User:
    def __init__(self, username: str, password: str, user_id: int, event_man: Eventmanager):
        self.username = username
        self.id = user_id
        self.password = password
        self.session: EventLogicalEndpoint = EventLogicalEndpoint(event_man)
