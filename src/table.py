"""
    This file defines a Table class, which encapsulates a Stratego game state,
    enrich it with time control, methods to manage users interactions with the table,

"""
from __future__ import annotations

from typing import Callable, Tuple

from src.ProtocolObjects import ParsingException, PieceToken, Move
from src.ResourceManager import ResourceManagerJob, DelayedTask, ResourceManager, process_time_ms
from src.User import User
from src.stratego import *


class UserTableRole(Enum):
    spectator = 0
    red_player = 1
    blue_player = 2


class TableGamePhase(Enum):
    awaiting = 0
    setup = 1
    gameplay = 2
    finished = 3


class TableTimeControl:
    def __init__(self, setup_time_ms: int, red_base_time_ms: int,
                 blue_base_time_ms: int, red_increment_ms=0, blue_increment_ms=0):
        self.red_time_control_ms = red_base_time_ms, red_increment_ms
        self.blue_time_control_ms = blue_base_time_ms, blue_increment_ms
        self.setup_time_ms = setup_time_ms


class _TablePhase:

    def __init__(self, phase_init: Callable, phase_logic: Callable, phase_finish: Callable):
        self._phase_init = phase_init
        self._phase_logic = phase_logic
        self._phase_finish = phase_finish

    def init(self):
        self._phase_init()

    def logic(self):
        self._phase_logic()

    def finish(self):
        self._phase_finish()


class _SeatManager:
    """
    Note: This class performs an immediate transmission between awaiting phase and setup phase
    after gathering full seating. While this would be preferable for automated match making,
    it may be not desirable behavior for seating players in private or public rooms.

    For custom behaviour, please use subclass of this
    """

    def __init__(self, set_table_to_setup_phase: Callable, seat_observer: Callable[[int, Side | None], any]):
        self.seats: dict[Side, None | int] = {Side.red: None, Side.blue: None}
        self._set_table_to_setup_phase = set_table_to_setup_phase
        self._seat_observer = seat_observer

    def _phase_init(self, clear_seats=True):
        if clear_seats:
            self.seats = {Side.red: None, Side.blue: None}

    def _phase_logic(self):
        if self.seats[Side.blue] is not None and self.seats[Side.red] is not None:
            self._set_table_to_setup_phase()

    def _phase_finish(self):
        pass

    def get_phase(self, clear_seats: bool = True) -> _TablePhase:
        return _TablePhase(lambda: self._phase_init(clear_seats), self._phase_logic, self._phase_finish)

    def take_seat(self, user_id, color: Side) -> tuple[bool, str | None]:
        if self.seats[color] is not None:
            return False, "Seat is already taken"
        self.seats[color] = user_id
        self._seat_observer(user_id, color)
        return True, None

    def get_side(self, user_id) -> Side | None:
        if user_id not in self.seats.values():
            return None
        return Side.red if self.seats[Side.red] == user_id else Side.blue

    def release_seat(self, user_id) -> tuple[bool, str | None]:
        if user_id not in self.seats.values():
            return False, "Seat does not exist"
        for k, v in self.seats.items():
            if v == user_id:
                self.seats[k] = None
        self._seat_observer(user_id, None)
        return True, None

    def swap_seats(self):
        self.seats = {k.flip(): v for k, v in self.seats.items()}
        for k in Side:
            if self.seats[k] is not None:
                self._seat_observer(self.seats[k], k)


class _SeatManagerWithReadyCommand(_SeatManager):
    """
        Extends seat manager to allow players to set their readiness status.
        Instead of starting game automatically after taking both seats are taken,
        this seat manager will wait for both players to set their ready flag to true.
        After this flag is seat, seat manager will wait transmission_time_ms ms to give
        user chance to change their mind.
    """

    def __init__(self, set_table_to_setup_phase: Callable,
                 resource_manager: ResourceManager, transmission_time_ms: int,
                 seat_observer: Callable[[int, Side], any]):
        super().__init__(set_table_to_setup_phase, seat_observer)
        self._readiness: dict[Side, bool] = {Side.red: False, Side.blue: False}
        self._transmission_task: DelayedTask | None = None
        self.resource_manager = resource_manager
        self._transmission_time_ms = transmission_time_ms

    def _phase_init(self, clear_seats: bool = True):
        self._readiness = {Side.red: False, Side.blue: False}
        super()._phase_init(clear_seats)

    def _phase_logic(self):
        if self._readiness[Side.red] and self._readiness[Side.blue] and self._transmission_task is None:
            self._transmission_task = DelayedTask(lambda: self._set_table_to_setup_phase(),
                                                  self._transmission_time_ms)
            self.resource_manager.add_delayed_task(self._transmission_task)

    def _phase_finish(self):
        if self._transmission_task is not None:
            self._transmission_task.cancel()
        super()._phase_finish()

    def release_seat(self, user_id) -> tuple[bool, str | None]:
        if user_id not in self.seats.values():
            return False, "Seat does not exist"
        for k, v in self.seats.items():
            if v == user_id:
                self.seats[k] = None
                self._readiness[k] = False
        if self._transmission_task is not None:
            self._transmission_task.cancel()
            self._transmission_task = None
        self._seat_observer(user_id, None)
        return True, None

    def set_readiness(self, user_id, value: bool) -> tuple[bool, str | None]:
        side = self.get_side(user_id)
        if side is None:
            return False, "Seat does not exist"

        if not value and self._transmission_task is not None:
            self._transmission_task.cancel()
            self._transmission_task = None
        self._readiness[side] = value


class _SetupManager:
    def __init__(self, resource_manager: ResourceManager, time_for_setup_ms: int,
                 set_table_to_gameplay_mode: Callable[[list[Piece | None]], None],
                 set_table_to_finished_mode: Callable[[Side | None], None]):
        self.setups: dict[Side, dict[int, PieceType] | None] = {Side.red: None, Side.blue: None}
        self.__setup_timeout_task: DelayedTask | None = None
        self.__set_table_to_gameplay_mode = set_table_to_gameplay_mode
        self.__set_table_to_finished_mode = set_table_to_finished_mode
        self.time_for_setup_ms = time_for_setup_ms
        self.__resource_manager = resource_manager

    def propose_setup(self, color: Side, setup: dict[int, PieceType]) -> tuple[bool, str | None]:
        if not verify_setup_dict(setup, color):
            return False, "Proposed setup is not valid"
        self.setups[color] = setup
        return True, None

    def __on_timeout(self):
        blue_submitted = self.setups[Side.blue] is not None
        red_submitted = self.setups[Side.red] is not None
        if blue_submitted and red_submitted:
            self.__set_table_to_gameplay_mode(game_state_from_setups(self.setups[Side.red], self.setups[Side.blue]))
        else:
            winner = None
            if blue_submitted:
                winner = Side.blue
            if red_submitted:
                winner = Side.red
            self.__set_table_to_finished_mode(winner)

    def __phase_init(self):
        self.setups = {Side.red: None, Side.blue: None}
        self.__setup_timeout_task = DelayedTask(self.__on_timeout, self.time_for_setup_ms)
        self.__resource_manager.add_delayed_task(self.__setup_timeout_task)

    def __phase_logic(self):
        pass

    def __phase_finish(self):
        if self.__setup_timeout_task is not None:
            self.__setup_timeout_task.cancel()
            self.__setup_timeout_task = None

    def get_phase(self) -> _TablePhase:
        return _TablePhase(self.__phase_init, self.__phase_logic, self.__phase_finish)


class _GameplayManager:
    def __init__(self, resource_manager: ResourceManager, time_control: TableTimeControl,
                 set_table_to_finished_mode: Callable[[Side | None], None],
                 on_state_change: Callable[[], None]):
        self._game_state = GameState()
        self.__resource_manager = resource_manager
        self.__set_table_to_finished_mode = set_table_to_finished_mode
        self.__player_timeout_task: DelayedTask | None = None
        self.__time_budget: dict[Side:int] = {Side.red: time_control.red_time_control_ms[0],
                                              Side.blue: time_control.blue_time_control_ms[0]}
        self.time_control = time_control
        self.__turn_start: int = 0
        self.on_state_change = on_state_change

    def set_game_state(self, state: list[Piece | None]):
        self._game_state.set_game_state(state)

    def make_move(self, move: tuple[int, int], side: Side) -> tuple[bool, str | None]:

        if self._game_state.get_side() is not side:
            return False, "This is not your turn"

        if not self._game_state.is_move_legal(move):
            return False, "This is illegal move"

        if self.__player_timeout_task is not None:
            self.__player_timeout_task.cancel()
            self.__player_timeout_task = None

        tm_inc = self.time_control.red_time_control_ms if side is Side.red else self.time_control.blue_time_control_ms
        self.__time_budget[side] -= process_time_ms() - self.__turn_start
        self.__time_budget[side] += tm_inc[1]
        self._game_state.execute_move(move)

        return True, None

    def get_moving_side(self):
        return "blue" if self._game_state.get_side().value else "red"

    def get_view(self, perspective: Side | None):
        return self._game_state.get_view(perspective)

    def __player_timeout(self, side: Side):
        self.__set_table_to_finished_mode(side.flip())

    def __schedule_player_timeout(self):
        side_on_move = self._game_state.get_side()
        self.__player_timeout_task = DelayedTask(lambda: self.__player_timeout(side_on_move),
                                                 self.__time_budget[side_on_move])
        self.__turn_start = process_time_ms()
        self.__resource_manager.add_delayed_task(self.__player_timeout_task)

    def __phase_init(self, state: list[Piece | None]):
        self.set_game_state(state)
        self.__time_budget = {Side.red: self.time_control.red_time_control_ms[0],
                              Side.blue: self.time_control.blue_time_control_ms[0]}

    def __phase_logic(self):
        if self._game_state.is_game_finish():
            self.__set_table_to_finished_mode(self._game_state.get_winner())
        elif self.__player_timeout_task is None:
            self.__schedule_player_timeout()
            self.on_state_change()

    def __phase_finish(self):
        if self.__player_timeout_task is not None:
            self.__player_timeout_task.cancel()
            self.__player_timeout_task = None

    def get_phase(self, state: list[Piece | None]) -> _TablePhase:
        return _TablePhase(lambda: self.__phase_init(state), self.__phase_logic, self.__phase_finish)


class _FinishedStateManager:
    def __init__(self, execute_rematch: Callable):
        self.players_wanting_rematch: list[int] = []  # we are treating this list as a set
        self.__exec_rematch = execute_rematch

    def set_rematch_willingness(self, user: User, value: bool):
        if value:
            self.players_wanting_rematch = [user_id for user_id in self.players_wanting_rematch if user_id != user.id]
            self.players_wanting_rematch += [user.id]
        else:
            self.players_wanting_rematch = [user_id for user_id in self.players_wanting_rematch if user_id != user.id]

    def __phase_init(self):
        self.players_wanting_rematch = set()

    def __phase_logic(self):
        if len(self.players_wanting_rematch) == 2:
             self.__exec_rematch()

    def __phase_finish(self):
        pass

    def get_phase(self) -> _TablePhase:
        return _TablePhase(self.__phase_init, self.__phase_logic, self.__phase_finish)


class Table:
    class Builder:
        def __init__(self, resource_manager: ResourceManager):
            self.__resource_manager = resource_manager
            self.__time_control: TableTimeControl = TableTimeControl(300000, 1200000, 1200000)
            self.__use_readiness = True
            self.__start_timer = 10000
            self.__event_channels = {side: (lambda d: None) for side in {Side.red, Side.blue, None}}
            self.__seat_observer: Callable[[int, Side | None], any] = lambda x, y: None

        def get_sm_constructor(self):
            if self.__use_readiness:
                return lambda x: _SeatManagerWithReadyCommand(x, self.__resource_manager,
                                                              self.__start_timer, self.__seat_observer)
            else:
                return lambda x: _SeatManager(x, self.__seat_observer)

        def build(self) -> Table:
            return Table(self.__resource_manager, self.__time_control, self.get_sm_constructor(), self.__event_channels)

        def set_use_readiness(self, val: bool) -> Table.Builder:
            self.__use_readiness = val
            return self

        def set_start_timer(self, value_ms: int) -> Table.Builder:
            self.__start_timer = value_ms
            return self

        def set_setup_time(self, value_ms: int) -> Table.Builder:
            self.__time_control.setup_time_ms = value_ms
            return self

        def set_time_control(self, base_time_ms: int, increment_time_ms: int,
                             side: Side | None = None) -> Table.Builder:
            if side is Side.red or side is None:
                self.__time_control.red_time_control_ms = base_time_ms, increment_time_ms

            if side is Side.blue or side is None:
                self.__time_control.blue_time_control_ms = base_time_ms, increment_time_ms

            return self

        def set_event_channels(self, channels: [Side | None, Callable[[dict], any]]) -> Table.Builder:
            self.__event_channels = channels
            return self

        def set_seat_observer(self, seat_observer: Callable[[int, Side | None], any]) -> Table.Builder:
            self.__seat_observer = seat_observer
            return self

    def __init__(self, resource_manager: ResourceManager, time_control: TableTimeControl,
                 seat_manager_constructor: Callable[[Callable], _SeatManager],
                 event_channels: dict[Side | None, Callable[[dict], any]]):
        self.resource_manager = resource_manager
        self.phase_type: TableGamePhase = TableGamePhase.awaiting

        self._seat_manager = seat_manager_constructor(self.__change_phase_to_setup)
        self._setup_manager = _SetupManager(resource_manager, time_control.setup_time_ms,
                                            self.__change_phase_to_gameplay, self.__change_phase_to_finished)
        self._gameplay_manager = _GameplayManager(resource_manager, time_control, self.__change_phase_to_finished,
                                                  self.__send_state_change_event)
        self._finished_state_manager = _FinishedStateManager(self.__execute_rematch)
        self.__phase: _TablePhase = self._seat_manager.get_phase()
        self.__phase.init()
        self.__job = ResourceManagerJob(self.__phase.logic)
        self.__generated_events_counter = 0
        self.__event_channels = event_channels
        resource_manager.add_job(self.__job)

    def __del__(self):
        self.kill()

    def __change_phase(self, phase: _TablePhase):
        self.__phase.finish()
        self.__job.cancel()

        self.__phase = phase
        self.__phase.init()
        self.__job = ResourceManagerJob(self.__phase.logic)
        self.resource_manager.add_job(self.__job)

    def __change_phase_to_setup(self):
        self.__change_phase(self._setup_manager.get_phase())
        self.phase_type = TableGamePhase.setup
        self.__generate_event()

    def __change_phase_to_gameplay(self, state: list[Piece | None]):
        self.__change_phase(self._gameplay_manager.get_phase(state))
        self.phase_type = TableGamePhase.gameplay
        self.__generate_event()

    def __send_state_change_event(self):
        self.__generate_event()

    def __change_phase_to_finished(self, winner: Side | None):
        # TODO: Communicate winner to spectators
        # TODO: In future, we should save this data to database
        self.__change_phase(self._finished_state_manager.get_phase())
        self.phase_type = TableGamePhase.finished
        self.__generate_event()

    def __change_state_to_awaiting(self):
        self.__change_phase(self._seat_manager.get_phase(False))
        self.phase_type = TableGamePhase.awaiting
        self.__generate_event()

    def __execute_rematch(self):
        self._seat_manager.swap_seats()
        self.__change_phase_to_setup()

    def kill(self):
        self.__phase.finish()
        self.__job.cancel()

    def get_seat_manager(self):
        return self._seat_manager

    def get_setup_manager(self):
        return self._setup_manager

    def get_gameplay_manager(self):
        return self._gameplay_manager

    def remove_player(self, user_id):
        self.resign(user_id)
        result = self._seat_manager.release_seat(user_id)
        if result[0]:
            self.__change_state_to_awaiting()
        return result

    def resign(self, user_id):
        color = self._seat_manager.get_side(user_id)
        if color is None:
            return

        if self.phase_type is TableGamePhase.setup or self.phase_type is TableGamePhase.gameplay:
            self.__change_phase_to_finished(color.flip())

    def get_phase(self):
        return self.__phase

    def __generate_event(self):
        self.__generated_events_counter += 1
        status = {TableGamePhase.gameplay: "gameplay",
                  TableGamePhase.awaiting: "awaiting",
                  TableGamePhase.setup: "setup",
                  TableGamePhase.finished: "finished"}

        event_body = {"type": "board_event", "nr": self.__generated_events_counter, "status": status[self.phase_type],
                      "moving_side": self._gameplay_manager.get_moving_side()}

        for perspective in {Side.red, Side.blue, None}:
            event_body["board"] = self._gameplay_manager.get_view(perspective).get_view()
            self.__event_channels[perspective](event_body)

    def get_event_counter(self) -> int:
        return self.__generated_events_counter

    def get_finished_state_manager(self):
        return self._finished_state_manager


class TableApi:

    def __init__(self, table: Table):
        self.table = table

    def take_seat(self, request: dict, user: User) -> tuple[bool, str | None]:
        if self.table.phase_type is not TableGamePhase.awaiting:
            return False, "Table is not awaiting new players"

        color: str = request.get("side")

        if color not in ["blue", "red"]:
            return False, "Field side has invalid value"

        side = Side.red if color == "red" else Side.blue
        return self.table.get_seat_manager().take_seat(user.id, side)

    def submit_setup(self, request: dict, user: User) -> tuple[bool, str | None]:
        if self.table.phase_type is not TableGamePhase.setup:
            return False, "Table is not accepting setup at the moment"

        if user.id not in self.table.get_seat_manager().seats.values():
            return False, "Only players can do that"

        setup = request.get("setup")
        if type(setup) is not list:
            return False, f"Expected list found {type(setup)} instead"

        try:
            setup = [PieceToken.parse_from_dict(tok) for tok in setup]
            setup = {tok.sq: tok.get_piece_type() for tok in setup}
            color = Side.red if self.table.get_seat_manager().seats[Side.red] == user.id else Side.blue
            return self.table.get_setup_manager().propose_setup(color, setup)
        except ParsingException:
            return False, "Unable to parse setup"

    def make_move(self, request: dict, user: User) -> tuple[bool, str | None]:
        if self.table.phase_type is not TableGamePhase.gameplay:
            return False, "Table is not in playable phase"

        if user.id not in self.table.get_seat_manager().seats.values():
            return False, "Only players can do that"

        move = request.get("move")
        if type(move) is not dict:
            return False, f"Expected dict found {type(move)} instead"
        try:
            move = Move.parse_from_dict(move)
            color = Side.red if self.table.get_seat_manager().seats[Side.red] == user.id else Side.blue
            return self.table.get_gameplay_manager().make_move((move.from_, move.to_), color)
        except ParsingException:
            return False, "Unable to parse move"

    def resign(self, user: User) -> tuple[True, None]:
        self.table.resign(user.id)
        return True, None

    def leave_table(self, user: User) -> tuple[True, None]:
        self.table.remove_player(user.id)
        return True, None

    def set_readiness(self, request: dict, user: User) -> tuple[bool, str | None]:
        if self.table.phase_type is not TableGamePhase.awaiting:
            return False, "Table is not in accepting this command at this phase "

        value = request["value"]
        if type(value) is not bool:
            return False, f"Field value has incorrect type, expected bool found {type(value)}"

        seat_man = self.table.get_seat_manager()
        if isinstance(seat_man, _SeatManagerWithReadyCommand):
            return seat_man.set_readiness(user.id, value)

        return True, None

    def release_seat(self, user: User) -> tuple[bool, str]:
        if self.table.phase_type not in {TableGamePhase.awaiting, TableGamePhase.finished}:
            return False, "You can not release seat in this game phase, try resigning"

        return self.table.remove_player(user.id)

    def get_board(self, user: User) -> dict:
        # Maybe this method should be moved down, to a table api ?
        nr = self.table.get_event_counter()
        status = self.table.phase_type
        status = {TableGamePhase.gameplay: "gameplay",
                  TableGamePhase.awaiting: "awaiting",
                  TableGamePhase.setup: "setup",
                  TableGamePhase.finished: "finished"}[status]
        perspective = self.table.get_seat_manager().get_side(user.id)

        response = {"status": "success",
                    "nr": nr,
                    "game_status": status,
                    "moving_side": self.table.get_gameplay_manager().get_moving_side(),
                    "board": self.table.get_gameplay_manager().get_view(perspective).get_view()
                    }
        return response

    def set_rematch_willingness(self, user: User, request: dict) -> tuple[bool, str | None]:
        if self.table.phase_type is not TableGamePhase.finished:
            return False, "Game is not finished yet"

        if user.id not in self.table.get_seat_manager().seats.values():
            return False, "Only players can do that"

        value = request.get("value")

        if type(value) is not bool:
            return False, f'Expected field "value" to have type bool, found {type(value)} instead'

        self.table.get_finished_state_manager().set_rematch_willingness(user, value)

        return True, None
