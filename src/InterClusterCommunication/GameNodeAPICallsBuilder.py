from enum import Enum


class GameNodeAPICallCommands(Enum):
    GET_ROOM_METADATA = 0
    JOIN_ROOM = 1
    CREATE_ROOM = 2
    EXIT_ROOM = 3
    GET_USER_LIST = 4
    REQUEST_BOARD = 5
    TAKE_SEAT = 6
    RELEASE_SEAT = 7
    SET_READY = 8
    FETCH_CHAT_METADATA = 9
    FETCH_CHAT_MESSAGES = 10
    SEND_MESSAGE = 11
    SEND_PIECE_SETUP = 12
    MAKE_MOVE = 13
    RESIGN = 14
    LEAVE_ROOM = 15
    SET_REMATCH_WILLINGNESS = 16


_GameNodeAPICallCommandsToString: dict[GameNodeAPICallCommands, str] = {
    GameNodeAPICallCommands.GET_ROOM_METADATA: "get_room_info",
    GameNodeAPICallCommands.JOIN_ROOM: "join_room",
    GameNodeAPICallCommands.CREATE_ROOM: "create_room",
    GameNodeAPICallCommands.EXIT_ROOM: "exit_room",
    GameNodeAPICallCommands.GET_USER_LIST: "get_room_users",
    GameNodeAPICallCommands.REQUEST_BOARD: "get_board",
    GameNodeAPICallCommands.TAKE_SEAT: "claim_seat",
    GameNodeAPICallCommands.RELEASE_SEAT: "release_seat",
    GameNodeAPICallCommands.SET_READY: "set_ready",
    GameNodeAPICallCommands.FETCH_CHAT_METADATA: "get_chat_metadata",
    GameNodeAPICallCommands.FETCH_CHAT_MESSAGES: "get_chat_messages",
    GameNodeAPICallCommands.SEND_MESSAGE: "send_chat_message",
    GameNodeAPICallCommands.SEND_PIECE_SETUP: "send_setup",
    GameNodeAPICallCommands.MAKE_MOVE: "send_move",
    GameNodeAPICallCommands.RESIGN: "resign",
    GameNodeAPICallCommands.LEAVE_ROOM: "leave_room",
    GameNodeAPICallCommands.SET_REMATCH_WILLINGNESS: "set_rematch_willingness"
}


class GameNodeApiRequestFactory:
    def __init__(self):
        pass

    def create_get_room_info_request(self, room_id: str):
        req = {
            "message_id": "get_room_info_" + room_id,
            "type": _GameNodeAPICallCommandsToString[GameNodeAPICallCommands.GET_ROOM_METADATA],
            "room_id": room_id
        }
        return req

    def create_create_room_request(self, control_params: dict):
        req = {
            "message_id": "create_room",
            "type": _GameNodeAPICallCommandsToString[GameNodeAPICallCommands.CREATE_ROOM],
            "time_control": float(control_params.get("time_control")),
            "time_added": float(control_params.get("time_added")),
            "setup_time": float(control_params.get("setup_time"))
        }
        if control_params.get("password") is not None:
            req["password"] = control_params["password"]
        return req

    def create_join_room_request(self, control_params: dict, room_id: str):
        req = {
            "message_id": "join_room_" + room_id,
            "type": _GameNodeAPICallCommandsToString[GameNodeAPICallCommands.JOIN_ROOM],
            "room_id": room_id,
        }
        if control_params.get("password"):
            req["password"] = control_params["password"]
        return req
