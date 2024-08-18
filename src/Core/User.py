from src.Events.Events import EventLogicalEndpointWithSignature, Eventmanager


class User:
    def __init__(self, username: str, password: str, user_id: int,
                 event_man: Eventmanager, signature: str | None = None):
        self.username = username
        self.id = user_id
        self.password = password
        self.room_count = 0
        self.session: EventLogicalEndpointWithSignature =\
            EventLogicalEndpointWithSignature(event_man, username if signature is None else signature)


class UserDto:
    def __init__(self, username: str, password: str, user_id: int):
        self.username = username
        self.password = password
        self.user_id = user_id


class HttpUser:
    def __init__(self, username: str, password: str, user_id: int):
        self.username = username
        self.password = password
        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False
        self.user_id: str | None = str(user_id)

    def get_dto(self):
        return UserDto(self.username, self.password, int(self.user_id))

    @staticmethod
    def from_dto(dto: UserDto):
        return HttpUser(dto.username, dto.password, dto.user_id)

    def get_id(self):
        return self.user_id
