import enum

from src.Core.MessageSystem import MessageManager


class RoomMessagesCodes(enum.Enum):

    # 1 arg: phase: TableGamePhase
    # Request room change
    SET_ROOM_PHASE = 0

    # 1 arg: phase: TableGamePhase
    # The current active phase of the room has been changed
    ROOM_PHASE_CHANGED = 1

    # 2 arguments: player_side: Side, value: boolean
    # Sets ready in awaiting phase, allowing players to advance to 'setup' phase
    SET_READY_AWAITING_PHASE = 2

    # 2 arguments: player_side: Side, value: boolean
    # Sets ready in setup phase, allowing players to skip waiting to 'setup' phase time to run out.
    SET_READY_SETUP_PHASE = 3

    # no arguments
    GENERATE_BOARD_EVENT = 4

    # 2 arguments: player_username: string, event: string | jsonable dict
    FORWARD_EVENT_TO_USER = 5

    # 2 arguments: color: Side | None, time_ms: int
    PLAYER_TIMER_COUNTDOWN = 6

    # 2 arg: color: Side | None, value_ms[Optional]: int | None
    # Stops the specified player timer, with the specified time, or time remaining on the timer if not provided
    PLAYER_TIMER_STOP = 7

    # 1 argument: color: Side
    # Timer broadcast the player time has run down.
    # color := Side of user that has run out of time
    PLAYER_TIMER_HAS_STOPPED = 8


def create_message_manager() -> MessageManager:
    result: MessageManager = MessageManager()

    for _ in RoomMessagesCodes:
        result.register_msg()

    return result


if __name__ == "__main__":
    create_message_manager()
