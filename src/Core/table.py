"""
    This file defines a Table class, which encapsulates a Stratego game state,
    enrich it with time control, methods to manage users interactions with the table,

"""
from __future__ import annotations

import time
from enum import Enum
from math import floor
from typing import Callable

from src.Core.GameInstanceFactory import GameInstanceFactory
from src.Core.PlayerInfo import PlayerInfo, TimerMode, Timer
from src.Core.stratego_gamestate import verify_setup_dict, game_state_from_setups
from src.ProtocolObjects import ParsingException, PieceToken, Move
from src.Core.JobManager import Job, DelayedTask, JobManager, time_ms
from src.Core.User import User
from src.Core.stratego import *


class TableGamePhase(Enum):
    """
    Represents the different phases that a multiplayer game can be in, from waiting for players to join and set up
    their boards, to actively playing the game itself, to the final phase when the match has ended.

    :custom: This is a custom enum defined for this specific use case.
    """
    awaiting = 0
    setup = 1
    gameplay = 2
    finished = 3


class TableTimeControl:
    """
    Represents the time control settings for a multiplayer game, including the amount of time each player has to set
    up their board and make initial moves, as well as the base time limit and increment (if any) for each player
    during the gameplay phase.

    :custom: This is a custom class defined for this specific use case.
    """

    def __init__(self, setup_time_ms: int, red_base_time_ms: int,
                 blue_base_time_ms: int, red_increment_ms=0, blue_increment_ms=0):
        self.red_time_control_ms = red_base_time_ms, red_increment_ms
        self.blue_time_control_ms = blue_base_time_ms, blue_increment_ms
        self.setup_time_ms = setup_time_ms


class PlayerInfoManager:
    """
       This class manages players info.
    """
    def __init__(self):
        self.player_info = {s: PlayerInfo() for s in Side}
        self.on_player_info_change: Callable[[Side, PlayerInfo], any] = lambda x, y: None

    @abstractmethod
    def __sync_task_with_timer(self, func: Callable, timers: list[Timer]) -> Callable:
        def _(*args, **kwargs):
            for timer in timers:
                timer.mode = TimerMode.PAUSED
                timer.value = 0

            func(*args, **kwargs)

        return _

    def count_down_both_clocks(self, delay: int, on_time_runs_down: Callable) -> DelayedTask:
        result = DelayedTask(on_time_runs_down, delay)
        timers = [self.player_info[s].timer for s in Side]
        result.cancel = self.__sync_task_with_timer(result.cancel, timers)
        for timer in timers:
            timer.mode = TimerMode.COUNT_DOWN
            timer.value = floor(1000*time.time()) + delay

        return result


class TablePhase:
    """
    This class represents a phase in a table's execution. It is initialized with three callables: 1. `phase_init` -
    called at the beginning of the phase to prepare it. 2. `phase_logic` - called during the actual execution of the
    phase. 3. `phase_finish` - called at the end of the phase to perform any cleanup or finalization tasks. :param
    phase_init: A callable function that should not take any arguments and should be used to initialize the phase.
    :param phase_logic: A callable function that takes no arguments and performs the logic for this phase. :param
    phase_finish: A callable function that does not take any arguments and performs cleanup or finalization tasks at
    the end of the phase.
    """

    def __init__(self, phase_init: Callable, phase_logic: Callable, phase_finish: Callable):
        self._phase_init = phase_init
        self._phase_logic = phase_logic
        self._phase_finish = phase_finish

    def init(self) -> None:
        """
        Initializes the phase by calling its initialization function.
        :return: None
        """
        self._phase_init()

    def logic(self) -> None:
        """
        Executes the logic of this phase by calling its execution function.
        :return: None
        """
        self._phase_logic()

    def finish(self) -> None:
        """
        Performs any cleanup or finalization tasks at the end of the phase by calling its finalization function.
        :return: None
        """
        self._phase_finish()


class SeatManager:
    """
    Note: This class performs an immediate transmission between awaiting phase and setup phase
    after gathering full seating. While this would be preferable for automated match making,
    it may be not desirable behavior for seating players in private or public rooms.

    For custom behaviour, please use subclass of this

    :param set_table_to_setup_phase: A callable that sets the table to the setup phase.
    :param seat_observer: A callable that takes a player's ID and side as arguments and performs
                            some action, such as sending a notification to the player.
    """

    def __init__(self, set_table_to_setup_phase: Callable, seat_observer: Callable[[int, Side | None], any],
                 player_info_manager: PlayerInfoManager):
        self.seats: dict[Side, None | int] = {Side.red: None, Side.blue: None}
        self._set_table_to_setup_phase = set_table_to_setup_phase
        self._player_info_manager = player_info_manager
        self._seat_observer = seat_observer

    def _phase_init(self, clear_seats=True):
        """Initialization phase."""
        if clear_seats:
            self.seats = {Side.red: None, Side.blue: None}

    def _phase_logic(self):
        """Logic for the phase """
        if self.seats[Side.blue] is not None and self.seats[Side.red] is not None:
            self._set_table_to_setup_phase()

    def _phase_finish(self):
        """Finalization phase."""
        pass

    def get_phase(self, clear_seats: bool = True) -> TablePhase:
        """Returns the current table phase with initialization, logic, and finalization functions."""
        return TablePhase(lambda: self._phase_init(clear_seats), self._phase_logic, self._phase_finish)

    def take_seat(self, user_id, color: Side) -> tuple[bool, str | None]:
        """Takes a seat for the player with the given ID and color."""
        if self.seats[color] is not None:
            return False, "Seat is already taken"

        if self.seats[color.flip()] == user_id:
            self.release_seat(user_id)

        self.seats[color] = user_id
        self._seat_observer(user_id, color)
        return True, None

    def get_side(self, user_id) -> Side | None:
        """Returns the side of the player with the given ID or None if they are not seated."""
        if user_id not in self.seats.values():
            return None
        return Side.red if self.seats[Side.red] == user_id else Side.blue

    def release_seat(self, user_id) -> tuple[bool, str | None]:
        """Releases the seat of the player with the given ID."""
        if user_id not in self.seats.values():
            return False, "Seat does not exist"
        self.seats[self.get_side(user_id)] = None
        self._seat_observer(user_id, None)
        return True, None

    def swap_seats(self):
        """Swaps the seats of both players."""
        self.seats = {k.flip(): v for k, v in self.seats.items()}
        for k in Side:
            if self.seats[k] is not None:
                self._seat_observer(self.seats[k], k)


class SeatManagerWithReadyCommand(SeatManager):
    """
        Extends seat manager to allow players to set their readiness status.
        Instead of starting game automatically after taking both seats are taken,
        this seat manager will wait for both players to set their ready flag to true.
        After this flag is seat, seat manager will wait transmission_time_ms ms to give
        user chance to change their mind.

        :param set_table_to_setup_phase: Callable that sets the table to setup phase. :param job_manager: JobManager
        instance used for delayed tasks management. :param transmission_time_ms: Delay (in milliseconds) after both
        players are ready and before game starts. :param on_ready_change: Callback function taking Side and boolean
        as arguments, called when readiness is changed :param seat_observer: Callback function taking seat ID and
        Side as arguments, called when a seat is released or occupied.
    """

    def __init__(self, set_table_to_setup_phase: Callable,
                 job_manager: JobManager, transmission_time_ms: int,
                 on_ready_change: Callable[[Side, bool], any],
                 seat_observer: Callable[[int, Side], any],
                 player_info_manager: PlayerInfoManager):
        super().__init__(set_table_to_setup_phase, seat_observer, player_info_manager)
        self._on_ready_change = on_ready_change
        self._readiness: dict[Side, bool] = {Side.red: False, Side.blue: False}
        self._transmission_task: DelayedTask | None = None
        self.job_manager = job_manager
        self._transmission_time_ms = transmission_time_ms

    def _phase_init(self, clear_seats: bool = True):
        """Initialize phase."""
        self._readiness = {Side.red: False, Side.blue: False}
        super()._phase_init(clear_seats)

    def _phase_logic(self):
        """Main game logic in active phase."""
        if self._readiness[Side.red] and self._readiness[Side.blue] and self._transmission_task is None:
            task = DelayedTask(lambda: self._set_table_to_setup_phase(), self._transmission_time_ms)
            self.job_manager.add_delayed_task(task)
            self._transmission_task = task

    def _phase_finish(self):
        """Clean up phase."""
        if self._transmission_task is not None:
            self._transmission_task.cancel()
        super()._phase_finish()

    def release_seat(self, user_id) -> tuple[bool, str | None]:
        """Release seat occupied by user"""
        if user_id not in self.seats.values():
            return False, "Seat does not exist"
        for k, v in self.seats.items():
            if v == user_id:
                self.seats[k] = None
                self._readiness[k] = False
                self._on_ready_change(k, False)

        if self._transmission_task is not None:
            self._transmission_task.cancel()
            self._transmission_task = None
        self._seat_observer(user_id, None)
        return True, None

    def set_readiness(self, user_id, value: bool) -> tuple[bool, str | None]:
        """Set readiness flag for specified user"""
        side = self.get_side(user_id)
        if side is None:
            return False, "Seat does not exist"

        if not value and self._transmission_task is not None:
            self._transmission_task.cancel()
            self._transmission_task = None
        self._readiness[side] = value
        self._on_ready_change(side, value)
        return True, None

    def get_readiness(self):
        """Get readiness status of all players."""
        result = {
            "status": "success",
            "red_player": self._readiness[Side.red],
            "blue_player": self._readiness[Side.blue]
        }
        return result


class SetupManager:
    def __init__(self, job_manager: JobManager, time_for_setup_ms: int,
                 set_table_to_gameplay_mode: Callable[[GameState], None],
                 set_table_to_finished_mode: Callable[[Side | None], None],
                 player_info_manager: PlayerInfoManager):
        self.setups: dict[Side, dict[int, PieceType] | None] = {Side.red: None, Side.blue: None}
        self.__setup_timeout_task: DelayedTask | None = None
        self.__set_table_to_gameplay_mode = set_table_to_gameplay_mode
        self.__set_table_to_finished_mode = set_table_to_finished_mode
        self.time_for_setup_ms = time_for_setup_ms
        self.__job_manager = job_manager
        self.__player_info_manager: PlayerInfoManager = player_info_manager

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
        self.__setup_timeout_task = self.__player_info_manager.count_down_both_clocks(self.time_for_setup_ms,
                                                                                      self.__on_timeout)
        self.__job_manager.add_delayed_task(self.__setup_timeout_task)

    def __phase_logic(self):
        pass

    def __phase_finish(self):
        if self.__setup_timeout_task is not None:
            self.__setup_timeout_task.cancel()
            self.__setup_timeout_task = None

    def get_phase(self) -> TablePhase:
        return TablePhase(self.__phase_init, self.__phase_logic, self.__phase_finish)


class GameplayManager:
    def __init__(self, job_manager: JobManager, time_control: TableTimeControl,
                 set_table_to_finished_mode: Callable[[Side | None], None],
                 on_state_change: Callable[[], None],
                 player_info_manager: PlayerInfoManager):
        self._game_instance = GameInstanceFactory().create_default()
        self.__job_manager = job_manager
        self.__set_table_to_finished_mode = set_table_to_finished_mode
        self.__player_timeout_task: DelayedTask | None = None
        self.__time_budget: dict[Side:int] = {Side.red: time_control.red_time_control_ms[0],
                                              Side.blue: time_control.blue_time_control_ms[0]}
        self.__player_info_manager = player_info_manager
        self.time_control = time_control
        self.__turn_start: int = 0
        self.on_state_change = on_state_change

    def set_game_state(self, state: GameState):
        self._game_instance.set_game_state(state)

    def make_move(self, move: tuple[int, int], side: Side) -> tuple[bool, str | None]:

        if self._game_instance.get_side() is not side:
            return False, "This is not your turn"

        if not self._game_instance.is_move_legal(move):
            return False, "This is illegal move"

        if self.__player_timeout_task is not None:
            self.__player_timeout_task.cancel()
            self.__player_timeout_task = None

        tm_inc = self.time_control.red_time_control_ms if side is Side.red else self.time_control.blue_time_control_ms
        self.__time_budget[side] -= time_ms() - self.__turn_start
        self.__time_budget[side] += tm_inc[1]
        self.__player_info_manager.player_info[side].timer.set_paused_value(self.__time_budget[side])
        self._game_instance.execute_move(move)

        return True, None

    def get_moving_side(self):
        return "blue" if self._game_instance.get_side().value else "red"

    def get_view(self, perspective: Side | None):
        return self._game_instance.get_view(perspective)

    def get_move_list(self, perspective: Side | None) -> list[dict]:
        if perspective is None or perspective is not self._game_instance.get_side():
            return []
        result = self._game_instance.move_gen(self._game_instance.get_side())
        return [Move(from_, to_).to_dict() for from_, to_ in result]

    def __player_timeout(self, side: Side):
        self.__set_table_to_finished_mode(side.flip())

    def __schedule_player_timeout(self):
        side_on_move = self._game_instance.get_side()
        timer = self.__player_info_manager.player_info[side_on_move].timer
        self.__player_timeout_task = timer.count_down(self.__time_budget[side_on_move],
                                                      lambda: self.__player_timeout(side_on_move))
        self.__turn_start = time_ms()
        self.__job_manager.add_delayed_task(self.__player_timeout_task)

    def __phase_init(self, state: GameState):
        self.set_game_state(state)
        self.__time_budget = {Side.red: self.time_control.red_time_control_ms[0],
                              Side.blue: self.time_control.blue_time_control_ms[0]}
        for s in Side:
            self.__player_info_manager.player_info[s].timer.set_paused_value(self.__time_budget[s])

    def __phase_logic(self):
        if self._game_instance.is_game_finish():
            self.__set_table_to_finished_mode(self._game_instance.get_winner())
        elif self.__player_timeout_task is None:
            self.__schedule_player_timeout()
            self.on_state_change()

    def __phase_finish(self):
        if self.__player_timeout_task is not None:
            self.__player_timeout_task.cancel()
            self.__player_timeout_task = None

    def get_phase(self, state: GameState) -> TablePhase:
        return TablePhase(lambda: self.__phase_init(state), self.__phase_logic, self.__phase_finish)


class FinishedStateManager:
    def __init__(self, execute_rematch: Callable, on_rematch_willingness_change: Callable):
        self.players_wanting_rematch: list[int] = []  # we are treating this list as a set
        self.winner: None | Side = None
        self.__on_change = on_rematch_willingness_change
        self.__exec_rematch = execute_rematch

    def set_rematch_willingness(self, user: User, value: bool):
        if value:
            self.players_wanting_rematch = [user_id for user_id in self.players_wanting_rematch if user_id != user.id]
            self.players_wanting_rematch += [user.id]
        else:
            self.players_wanting_rematch = [user_id for user_id in self.players_wanting_rematch if user_id != user.id]
        self.__on_change(self.players_wanting_rematch)

    def __phase_init(self):
        self.players_wanting_rematch = []
        self.__on_change(self.players_wanting_rematch)  # for second rematch

    def __phase_logic(self):
        if len(self.players_wanting_rematch) == 2:
            self.__exec_rematch()

    def __phase_finish(self):
        pass

    def get_phase(self) -> TablePhase:
        return TablePhase(self.__phase_init, self.__phase_logic, self.__phase_finish)


class Table:
    class Builder:
        def __init__(self, job_manager: JobManager):
            self.__job_manager = job_manager
            self.__time_control: TableTimeControl = TableTimeControl(300000, 1200000, 1200000)
            self.__use_readiness = True
            self.__start_timer = 10000
            self.__event_broadcast: Callable[[dict], any] = lambda x: None
            self.__event_channels: dict[Side | None, Callable[[dict], any]] = \
                {side: (lambda d: None) for side in {Side.red, Side.blue, None}}
            self.__seat_observer: Callable[[int, Side | None], any] = lambda x, y: None
            self.__player_info_manager = PlayerInfoManager()

        def get_sm_constructor(self):
            def __on_ready_change(side: Side, value: bool):
                event = {
                    "type": "ready_event",
                    "side": "red" if side is Side.red else "blue",
                    "value": value
                }
                self.__event_broadcast(event)

            if self.__use_readiness:
                return lambda x: SeatManagerWithReadyCommand(x, self.__job_manager,
                                                             self.__start_timer, __on_ready_change,
                                                             self.__seat_observer, self.__player_info_manager)
            else:
                return lambda x: SeatManager(x, self.__seat_observer, self.__player_info_manager)

        def build(self) -> Table:
            return Table(self.__job_manager, self.__time_control, self.get_sm_constructor(),
                         self.__player_info_manager, self.__event_channels, self.__event_broadcast)

        def set_use_readiness(self, val: bool) -> Table.Builder:
            self.__use_readiness = val
            return self

        def set_start_timer(self, value_ms: int) -> Table.Builder:
            """
                Sets the initial value of timer to start game
                :param value_ms: Time between both players declaring readiness and playing the game
                :return: returns itself for method chaining
            """
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

        def set_event_channels(self, channels: dict[Side | None, Callable[[dict], any]]) -> Table.Builder:
            self.__event_channels = channels
            return self

        def set_event_broadcast(self, broadcast: Callable[[dict], any]) -> Table.Builder:
            self.__event_broadcast = broadcast
            return self

        def set_seat_observer(self, seat_observer: Callable[[int, Side | None], any]) -> Table.Builder:
            self.__seat_observer = seat_observer
            return self

    def __init__(self, job_manager: JobManager, time_control: TableTimeControl,
                 seat_manager_constructor: Callable[[Callable], SeatManager],
                 player_info_manager: PlayerInfoManager,
                 event_channels: dict[Side | None, Callable[[dict], any]],
                 event_broadcast:  Callable[[dict], any]):
        self.job_manager = job_manager
        self.phase_type: TableGamePhase = TableGamePhase.awaiting

        self._player_info_manager = player_info_manager
        self._seat_manager = seat_manager_constructor(self.__change_phase_to_setup)
        self._setup_manager = SetupManager(job_manager, time_control.setup_time_ms,
                                           self.__change_phase_to_gameplay, self.__change_phase_to_finished,
                                           self._player_info_manager)
        self._gameplay_manager = GameplayManager(job_manager, time_control, self.__change_phase_to_finished,
                                                 self.__send_state_change_event, self._player_info_manager)
        self._finished_state_manager = FinishedStateManager(self.__execute_rematch, self.__rematch_listener)
        self.__phase: TablePhase = self._seat_manager.get_phase()
        self.__phase.init()
        self.__job = Job(self.__phase.logic)
        self.__generated_events_counter = 0
        self.__event_channels = event_channels
        self.__event_broadcast = event_broadcast
        job_manager.add_job(self.__job)

    def __del__(self):
        self.kill()

    def __change_phase(self, phase: TablePhase):
        self.__phase.finish()
        self.__job.cancel()

        self.__phase = phase
        self.__phase.init()
        self.__job = Job(self.__phase.logic)
        self.job_manager.add_job(self.__job)

    def __change_phase_to_setup(self):
        self._finished_state_manager.winner = None
        self.__change_phase(self._setup_manager.get_phase())
        self.phase_type = TableGamePhase.setup
        self.__generate_event()

    def __change_phase_to_gameplay(self, state: GameState):
        self._finished_state_manager.winner = None
        self.__change_phase(self._gameplay_manager.get_phase(state))
        self.phase_type = TableGamePhase.gameplay
        self.__generate_event()

    def __send_state_change_event(self):
        self.__generate_event()

    def __rematch_listener(self, rematch_list: list[int]):
        sides = [self._seat_manager.get_side(id_) for id_ in rematch_list]
        sides_str = [("red" if s is Side.red else "blue") for s in sides]
        event = {
            "type": "rematch_event",
            "rematch_willingness": sides_str
        }
        self.__event_broadcast(event)

    def __change_phase_to_finished(self, winner: Side | None):
        # TODO: In future, we should save this data to database
        self._finished_state_manager.winner = winner
        self.__change_phase(self._finished_state_manager.get_phase())
        self.phase_type = TableGamePhase.finished
        self.__generate_event()

    def __change_state_to_awaiting(self):
        self._finished_state_manager.winner = None
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
        if result[0] and self.phase_type is not TableGamePhase.awaiting:
            self.__change_state_to_awaiting()
        return result

    def resign(self, user_id):
        color = self._seat_manager.get_side(user_id)
        if color is None:
            return

        self._player_info_manager.player_info[color].set_user(None)

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

        winner = {Side.red: "red",
                  Side.blue: "blue",
                  None: None}[self._finished_state_manager.winner]

        event_body = {"type": "board_event", "nr": self.__generated_events_counter,
                      "game_status": status[self.phase_type],
                      "moving_side": self._gameplay_manager.get_moving_side(),
                      "red_clock": self._player_info_manager.player_info[Side.red].timer.to_dict(),
                      "blue_clock": self._player_info_manager.player_info[Side.blue].timer.to_dict(),
                      "winner": winner
                      }

        for perspective in {Side.red, Side.blue, None}:
            event_body["board"] = self._gameplay_manager.get_view(perspective).get_view()
            event_body["move_list"] = self._gameplay_manager.get_move_list(perspective)
            self.__event_channels[perspective](event_body)

    def get_event_counter(self) -> int:
        return self.__generated_events_counter

    def get_finished_state_manager(self):
        return self._finished_state_manager

    def get_player_info_manager(self):
        return self._player_info_manager


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
        result = self.table.get_seat_manager().take_seat(user.id, side)

        if result[0]:
            self.table.get_player_info_manager().player_info[side].set_user(user)

        return result

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
        if isinstance(seat_man, SeatManagerWithReadyCommand):
            return seat_man.set_readiness(user.id, value)
        else:
            return False, f"This room do not support this command"

    def get_player_readiness(self, user: User) -> tuple[bool, str | None] | dict:
        seat_man = self.table.get_seat_manager()
        if not isinstance(seat_man, SeatManagerWithReadyCommand):
            return False, f"This room do not support this command"
        return seat_man.get_readiness()

    def release_seat(self, user: User) -> tuple[bool, str]:
        if self.table.phase_type not in {TableGamePhase.awaiting, TableGamePhase.finished}:
            return False, "You can not release seat in this game phase, try resigning"

        return self.table.remove_player(user.id)

    def get_board(self, user: User) -> dict:
        nr = self.table.get_event_counter()
        status = self.table.phase_type
        status = {TableGamePhase.gameplay: "gameplay",
                  TableGamePhase.awaiting: "awaiting",
                  TableGamePhase.setup: "setup",
                  TableGamePhase.finished: "finished"}[status]
        perspective = self.table.get_seat_manager().get_side(user.id)
        move_list = self.table.get_gameplay_manager().get_move_list(perspective)

        winner = {Side.red: "red",
                  Side.blue: "blue",
                  None: None}[self.table.get_finished_state_manager().winner]

        response = {"status": "success",
                    "nr": nr,
                    "game_status": status,
                    "moving_side": self.table.get_gameplay_manager().get_moving_side(),
                    "board": self.table.get_gameplay_manager().get_view(perspective).get_view(),
                    "red_clock": self.table.get_player_info_manager().player_info[Side.red].timer.to_dict(),
                    "blue_clock": self.table.get_player_info_manager().player_info[Side.blue].timer.to_dict(),
                    "move_list": move_list,
                    "winner": winner
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

    def get_rematch_willingness(self) -> tuple[bool, str | None] | dict[str, any]:
        if self.table.phase_type is not TableGamePhase.finished:
            return False, "Game is not finished yet"

        ids = self.table.get_finished_state_manager().players_wanting_rematch
        seat_man = self.table.get_seat_manager()
        sides = [seat_man.get_side(id_) for id_ in ids]
        return {
            "status": "success",
            "rematch_willingness": [("red" if s is Side.red else "blue") for s in sides]
        }
