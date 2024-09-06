import random
import unittest
import unittest.mock as mock
from TestUtil.MainLoopStub import MainLoopStub
from TestUtil.UserSimulation import UserSimulationInterpreter
from TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator
from UnitTests.TestUtil.stratego_helpers import generate_random_setup, rand_move, FastWinPosition, \
    setup_to_protocol_form
from src.Core.table import *
from src.Core.table import (TablePhase, SeatManager, SetupManager, GameplayManager,
                            SeatManagerWithReadyCommand, FinishedStateManager)
from src.Core.stratego_gamestate import game_state_from_setups
from src.Events.Events import Eventmanager


class TestTablePhase(unittest.TestCase):
    def test(self):
        init_spy = mock.Mock()
        logic_spy = mock.Mock()
        finish_spy = mock.Mock()
        phase = TablePhase(init_spy, logic_spy, finish_spy)
        phase.init()
        self.assertTrue(init_spy.called, "Init function was not called")
        phase.logic()
        self.assertTrue(logic_spy.called, "Logic function was not called")
        phase.finish()
        self.assertTrue(finish_spy.called, "Finish function was not called")


class TestSeatManager(unittest.TestCase):

    def setUp(self):
        self.transmission_to_setup_phase = mock.Mock()
        self.seat_observer = mock.Mock()
        self.seat_manager = SeatManager(self.transmission_to_setup_phase, self.seat_observer)

    def tearDown(self):
        del self.transmission_to_setup_phase, self.seat_manager, self.seat_observer

    def test_phase_init(self):
        """
            Scenario: seat_manager get_phase(clear).init() should clear seats only if flag clear is set to true
        """
        for clear in [True, False]:
            self.seat_manager.seats[Side.red] = 7
            self.seat_manager.get_phase(clear).init()
            self.assertEqual(self.seat_manager.seats[Side.red] is None, clear)

    def test_phase_logic(self):
        """
            Scenario: seat_manager get_phase().logic() should call 'transmission_to_setup_phase' only if both seats are
            taken
        """
        testcases = [{Side.red: None, Side.blue: None}, {Side.red: None, Side.blue: 1}, {Side.red: 2, Side.blue: None},
                     {Side.red: 2, Side.blue: 1}]
        for i, case in enumerate(testcases):
            self.seat_manager.seats = case
            self.seat_manager.get_phase().logic()
            self.assertEqual(i == 3, self.transmission_to_setup_phase.called)

    def test_take_empty_seat(self):
        """
            Scenario: User takes an empty seat.

            Expected outcome:
            1. seat_manager.get_side(color) should return id of user
            2. seat_observer is called with arguments (user_id, color)

        :return:
        """
        testcases = (random.randint(1, 10), Side.red), (random.randint(11, 20), Side.blue)
        for case in testcases:
            user_id, color = case
            self.seat_manager.take_seat(user_id, color)
            self.assertIs(self.seat_manager.get_side(user_id), color)
            self.assertTrue(self.seat_observer.called)
            observers_args = self.seat_observer.call_args.args
            self.assertEqual(observers_args[0], user_id)
            self.assertEqual(observers_args[1], color)

    def test_seat_release(self):
        """
            Scenario: User releases seat which he is owning

            Expected outcome:
            1.  seat_manager.get_side(color) should return None
            2. seat_observer is called with arguments (user_id, None)
        """
        self.seat_manager.seats[Side.red] = 1
        self.seat_manager.seats[Side.blue] = 2
        for side in Side:
            user_id = self.seat_manager.seats[side]
            self.seat_manager.release_seat(user_id)
            self.assertIs(self.seat_manager.get_side(user_id), None)
            self.assertTrue(self.seat_observer.called)
            observers_args = self.seat_observer.call_args.args
            self.assertEqual(observers_args[0], user_id)
            self.assertEqual(observers_args[1], None)

    def test_take_empty_seat_while_already_owning_one(self):
        """
            Scenario: Users that has already seat tries to claim the other seat

            Expected outcome:
            - seat_manager.release_seat(user_id) is called during execution
            - seat_manager.seats[old_seat] is None
        """
        self.seat_manager.release_seat = mock.Mock(side_effect=self.seat_manager.release_seat)
        self.seat_manager.take_seat(1, Side.red)
        self.seat_manager.take_seat(1, Side.blue)
        self.assertTrue(self.seat_manager.release_seat.called)
        self.assertEqual(self.seat_manager.seats[Side.blue], 1)
        self.assertIs(self.seat_manager.seats[Side.red], None)

    def test_take_not_empty_seat(self):
        """
        Scenario: Users tries to claim seat taken by other player
        Expected outcome: take_seat returns (False, _)
        """
        self.seat_manager.take_seat(1, Side.red)
        self.assertFalse(self.seat_manager.take_seat(2, Side.red)[0])

    def test_release_seat_not_belonging_to_user(self):
        """
                Scenario: Users tries to release seat while not owning any
                Expected outcome: take_seat returns (False, _)
        """
        self.assertFalse(self.seat_manager.release_seat(2)[0])

    def test_swap_seats(self):

        self.seat_manager.take_seat(1, Side.red)
        self.seat_manager.take_seat(2, Side.blue)
        self.seat_manager.swap_seats()
        self.assertIs(self.seat_manager.get_side(1), Side.blue)
        self.assertIs(self.seat_manager.get_side(2), Side.red)


class TestSeatManagerWithReadyCommand(unittest.TestCase):

    def setUp(self):
        self.transmission_to_setup_phase = mock.Mock()
        self.seat_observer = mock.Mock()
        self.on_ready_change = mock.Mock()
        self.job_manager = JobManager()
        self.transmission_time = 50
        self.seat_manager = SeatManagerWithReadyCommand(self.transmission_to_setup_phase,
                                                        self.job_manager,
                                                        self.transmission_time,
                                                        self.on_ready_change,
                                                        self.seat_observer)

    def tearDown(self):
        del self.transmission_to_setup_phase, self.seat_manager, self.seat_observer
        del self.on_ready_change, self.job_manager

    def __start_transmission(self):
        self.seat_manager.get_phase().init()
        self.seat_manager.take_seat(1, Side.red)
        self.seat_manager.set_readiness(1, True)
        self.seat_manager.take_seat(2, Side.blue)
        self.seat_manager.set_readiness(2, True)
        self.seat_manager.get_phase().logic()

    def __wait_for_transmission(self):
        stop = DelayedTask(self.job_manager.kill, 2 * self.transmission_time)
        self.job_manager.add_delayed_task(stop)
        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()

    def test_phase_init(self):
        """
            Scenario: seat_manager get_phase().init() should clear ready status of seats
        """
        self.seat_manager.take_seat(1, Side.red)
        self.seat_manager.set_readiness(1, True)
        self.seat_manager.take_seat(2, Side.blue)
        self.seat_manager.set_readiness(2, True)
        self.seat_manager.get_phase().init()
        res = self.seat_manager.get_readiness()
        self.assertFalse(res.get("red_player"))
        self.assertFalse(res.get("blue_player"))

    def test_phase_logic(self):
        """
        Scenario:  seat_manager.get_phase().logic() should add delayed task to jobManger if both players are ready.
                   So after transmission_time ms  have passed, transmission to setup should have been called
        """
        self.__start_transmission()  # calls phase's init() and logic()
        self.__wait_for_transmission()

        self.assertTrue(self.transmission_to_setup_phase.called)

    def test_phase_finish(self):
        """
        Scenario: seat_manager.get_phase().logic() should add delayed task to jobManger if both players are ready
                   seat_manager.get_phase().finish() should call cancel on DelayedTask produced by manager
        """
        self.__start_transmission()
        self.seat_manager.get_phase().finish()
        self.__wait_for_transmission()
        self.assertFalse(self.transmission_to_setup_phase.called)

    def test_release_seat_cancels_transmission(self):
        """
            Scenario: after time began ticking for transmission to setup, releasing seat stops that transmission
        """
        self.__start_transmission()
        self.seat_manager.release_seat(1)
        self.__wait_for_transmission()
        self.assertFalse(self.transmission_to_setup_phase.called)

    def test_release_seat(self):
        """
            Test if release seat behaves the same as base class
        """
        self.seat_manager.take_seat(1, Side.red)
        self.seat_manager.take_seat(2, Side.blue)
        for side in Side:
            user_id = self.seat_manager.seats[side]
            self.seat_manager.release_seat(user_id)
            self.assertIs(self.seat_manager.get_side(user_id), None)
            self.assertTrue(self.seat_observer.called)
            observers_args = self.seat_observer.call_args.args
            self.assertEqual(observers_args[0], user_id)
            self.assertEqual(observers_args[1], None)


class TestSetupManager(unittest.TestCase):
    def setUp(self):
        self.job_manager = JobManager()
        self.setup_time = 50
        self.set_to_gameplay = mock.Mock()
        self.set_to_finish = mock.Mock()

        self.setup_manager = SetupManager(self.job_manager, self.setup_time,
                                          self.set_to_gameplay, self.set_to_finish)

    def tearDown(self):
        del self.setup_manager, self.job_manager, self.setup_time, self.set_to_finish, self.set_to_gameplay

    def __wait_for_transmission(self):
        stop = DelayedTask(self.job_manager.kill, 2 * self.setup_time)
        self.job_manager.add_delayed_task(stop)
        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()

    def __start_transmission(self):
        self.setup_manager.get_phase().init()

    def test_phase_finish_stop_transmission(self):
        self.__start_transmission()
        self.setup_manager.get_phase().finish()
        self.__wait_for_transmission()
        self.assertFalse(self.set_to_finish.called)
        self.assertFalse(self.set_to_gameplay.called)

    def test_players_submit_valid_setups(self):
        self.__start_transmission()
        for side in Side:
            r, msg = self.setup_manager.propose_setup(side, generate_random_setup(side))
            self.assertTrue(r, msg)
        self.__wait_for_transmission()
        self.assertFalse(self.set_to_finish.called)
        self.assertTrue(self.set_to_gameplay.called)

    def test_only_one_player_proposed_setup(self):
        """
            Scenario: Only one player submitted their setup in time

            Expected outcome: game undergoes transmission to finished phase
        """
        self.__start_transmission()
        self.setup_manager.propose_setup(Side.red, generate_random_setup(Side.red))

        self.__wait_for_transmission()
        self.assertTrue(self.set_to_finish.called)
        self.assertFalse(self.set_to_gameplay.called)

    def test_no_player_proposed_setup(self):
        """
            Scenario: Both players did not submit their setups

            Expected outcome: game undergoes transmission to finished phase
        """
        self.__start_transmission()
        self.__wait_for_transmission()
        self.assertTrue(self.set_to_finish.called)
        self.assertFalse(self.set_to_gameplay.called)


class TestGameplayManager(unittest.TestCase):
    def setUp(self):
        self.job_manager = JobManager()
        self.time_con = TableTimeControl(0, 5000, 5000)
        self.set_to_finish = mock.Mock()
        self.on_state_change = mock.Mock()
        self.initial_state = game_state_from_setups(generate_random_setup(Side.red),
                                                    generate_random_setup(Side.blue))
        self.gameplay_manager = GameplayManager(self.job_manager, self.time_con,
                                                self.set_to_finish, self.on_state_change)

        self.phase = self.gameplay_manager.get_phase(
            self.initial_state
        )

    def tearDown(self):
        del self.gameplay_manager, self.phase, self.initial_state
        del self.job_manager, self.time_con, self.set_to_finish, self.on_state_change

    def test_phase_logic_calls_on_state_change(self):
        """
            Scenario: GameplayManager is initialized. It should invoke on_state_change callback exactly
            once.
        """
        self.phase.init()  # part of init
        self.phase.logic()  # part of init
        self.phase.logic()  # post init
        self.assertTrue(self.on_state_change.call_count == 1)

    def test_make_move_cause_async_invoke_of_on_state_change(self):
        """
            This testcase checks if 'make_move' calls on_state_change either implicitly or by
            phase.logic()
        """
        self.phase.init()
        self.phase.logic()  # first call to logic
        self.phase.logic()
        self.assertEqual(self.on_state_change.call_count, 1)
        state = GameInstance()
        state.set_game_state(self.initial_state)
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        move = rand_move(state, moving_side)
        res, msg = self.gameplay_manager.make_move(move, moving_side)
        self.assertTrue(res, msg)
        self.phase.logic()
        self.assertEqual(self.on_state_change.call_count, 2)

    def test_player_timeout(self):
        """
            Tests if player would be timeout after his time runs out
        """
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        self.phase.init()
        self.phase.logic()

        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()

        self.assertTrue(self.set_to_finish.called)
        args = self.set_to_finish.call_args.args
        self.assertIs(args[0], moving_side.flip())  # assert side on move has lost

    def test_player_wins(self):
        """
            Tests if player winning by capturing enemy flag 'triggers set_to_finish'.
            As py product, it also checks if make move success on valid move
        """
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        winning_pos = FastWinPosition(moving_side)
        del self.phase
        self.phase = self.gameplay_manager.get_phase(winning_pos.game_state)
        self.phase.init()
        self.phase.logic()
        status, msg = self.gameplay_manager.make_move(winning_pos.winning_move, moving_side)
        self.assertTrue(status, msg)
        self.phase.logic()
        self.assertTrue(self.set_to_finish.called)
        args = self.set_to_finish.call_args.args
        self.assertIs(args[0], moving_side)  # assert side on move has won

    def test_make_move_fails_on_illegal_move(self):
        m = (2, 1)
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        status, _ = self.gameplay_manager.make_move(m, moving_side)
        self.assertFalse(status)

    def test_make_move_fails_on_invalid_move(self):
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        winning_pos = FastWinPosition(moving_side.flip())
        del self.phase
        self.phase = self.gameplay_manager.get_phase(winning_pos.game_state)
        self.phase.init()
        self.phase.logic()
        status, msg = self.gameplay_manager.make_move(winning_pos.winning_move, moving_side)
        self.assertFalse(status, msg)

    def test_get_move_list_on_player_turn(self):
        self.phase.init()
        self.phase.logic()
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        self.assertNotEqual(len(self.gameplay_manager.get_move_list(moving_side)), 0)

    def test_get_move_list_on_opponent_turn_returns_empty_list(self):
        self.phase.init()
        self.phase.logic()
        moving_side = Side.red if self.gameplay_manager.get_moving_side() == 'red' else Side.blue
        self.assertEqual(len(self.gameplay_manager.get_move_list(moving_side.flip())), 0)

    def test_get_move_list_return_empty_if_moving_side_is_none(self):
        self.phase.init()
        self.phase.logic()
        self.assertEqual(len(self.gameplay_manager.get_move_list(None)), 0)


class TestFinishedGameManager(unittest.TestCase):
    def setUp(self):
        self.execute_rematch = mock.Mock()
        self.event_man = Eventmanager(JobManager())
        self.user1 = User("tester", "123", 1, self.event_man, None)
        self.user2 = User("tester2", "123", 2, self.event_man, None)
        self.finished_state_manager = FinishedStateManager(self.execute_rematch)

    def tearDown(self):
        del self.finished_state_manager, self.execute_rematch, self.event_man
        del self.user1, self.user2

    def test_phase_logic_executes_rematch_if_both_players_are_willing(self):
        self.finished_state_manager.get_phase().init()
        self.finished_state_manager.set_rematch_willingness(self.user1, True)
        self.finished_state_manager.set_rematch_willingness(self.user2, True)
        self.finished_state_manager.get_phase().logic()
        self.assertTrue(self.execute_rematch.called)

    def test_set_rematch_willingness_false(self):
        self.finished_state_manager.get_phase().init()
        self.finished_state_manager.set_rematch_willingness(self.user1, True)
        self.finished_state_manager.set_rematch_willingness(self.user1, False)
        self.finished_state_manager.set_rematch_willingness(self.user2, True)
        self.finished_state_manager.get_phase().logic()
        self.assertFalse(self.execute_rematch.called)


class TestTable(unittest.TestCase):
    def setUp(self):
        self.job_manager = JobManager()
        self.event_man = Eventmanager(self.job_manager)
        self.table_builder = Table.Builder(self.job_manager)
        self.event_broadcast = mock.Mock()
        self.event_channels = {
            Side.red: mock.Mock(), Side.blue: mock.Mock(), None: mock.Mock()
        }
        self.seat_observer = mock.Mock()
        self.table_builder.set_event_broadcast(self.event_broadcast).set_event_channels(self.event_channels)
        self.table_builder.set_seat_observer(self.seat_observer)
        self.table_builder.set_use_readiness(False)

        self.user1 = User("tester", '', 1, self.event_man, None)
        self.user2 = User("tester2", '', 2, self.event_man, None)

    def tearDown(self):
        del self.user1, self.user2
        del self.table_builder
        del self.event_man
        del self.job_manager
        del self.seat_observer
        del self.event_channels

    def test_table_starts_in_awaiting_phase(self):
        """
        Scenario: Freshly created table should be in awaiting phase
        """
        self.assertIs(self.table_builder.build().phase_type, TableGamePhase.awaiting)

    def _run_job_manager(self, start_time_ms: int):
        self.job_manager.add_delayed_task(DelayedTask(self.job_manager.kill, start_time_ms))
        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()


class TestTableAwaitPhase(TestTable):
    def setUp(self):
        super().setUp()
        self.req_claim_seat = lambda color: {
            "type": "claim_seat",
            "side": color
        }
        self.req_release_seat = {
            "type": "release_seat"
        }

    def tearDown(self):
        super().tearDown()
        del self.req_claim_seat

    def test_table_take_seat(self):
        """
            Scenario: Users try to claim seat

            Expected outcomes: both users successfully claim the seat
        """
        table = self.table_builder.build()
        table_api = TableApi(table)

        res, msg = table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(res, msg)

        res, msg = table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        self.assertTrue(res, msg)

    def test_table_take_seat2(self):
        """
            Scenario: Users try to claim seat owned by other player
            Expected outcome: Actions fails
        """
        table = self.table_builder.build()
        table_api = TableApi(table)

        res, msg = table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(res, msg)

        res, msg = table_api.take_seat(self.req_claim_seat('red'), self.user2)
        self.assertFalse(res)

    def test_table_take_seat3(self):
        """
            Scenario: User already has a seat but tries to claim another one
            Expected outcome: Seat observer was called 2 times, one time being result of forfeiting the old seat, second
             one being result of taking that free seat
        """
        table = self.table_builder.build()
        table_api = TableApi(table)

        res, msg = table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(res, msg)

        res, msg = table_api.take_seat(self.req_claim_seat('blue'), self.user1)
        self.assertTrue(res, msg)

        self.assertEqual(self.seat_observer.call_count, 3)
        expected_value = [Side.red, None, Side.blue]
        for i, args in enumerate(self.seat_observer.call_args_list):
            self.assertEqual(args.args[0], self.user1.id)
            self.assertIs(args.args[1], expected_value[i])

    def test_table_take_set_invokes_seat_observer(self):
        """
            Scenario: User claiming seats should invoke seat_observer callback

            Expected outcomes: seat observer passed to builder is invoked
        """
        table = self.table_builder.build()
        table_api = TableApi(table)

        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(self.seat_observer.called)
        args = self.seat_observer.call_args.args
        self.assertEqual(args[0], self.user1.id)
        self.assertEqual(args[1], Side.red)

        table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        self.assertEqual(self.seat_observer.call_count, 2)
        args = self.seat_observer.call_args.args
        self.assertEqual(args[0], self.user2.id)
        self.assertEqual(args[1], Side.blue)

    def test_table_release(self):
        """
            Scenario: Users takes a seat and then release it
            Expected outcome: Both actions invoke ready command
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        res, msg = table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(res, msg)
        res, msg = table_api.release_seat(self.user1)
        self.assertTrue(res, msg)

    def test_table_release2(self):
        """
            Scenario: Users tries to release seat without claiming it
            Expected outcome: actions fails
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        res, _ = table_api.release_seat(self.user1)
        self.assertFalse(res)

    def test_seat_release_invokes_seat_observer(self):
        """
        Scenario: Users forfeits seat
        Expected outcome: seat observer is invoked
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        table_api.release_seat(self.user1)
        self.assertEqual(self.seat_observer.call_count, 2)
        args = self.seat_observer.call_args.args
        self.assertEqual(args[0], self.user1.id)
        self.assertEqual(args[1], None)


class TestTableAwaitPhaseWithoutReadyCommand(TestTableAwaitPhase):
    def test_set_readiness_command_fails(self):
        """
        Scenario: Table was build without support for ready command but player invoke set readiness
        Expected outcome: command fails
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        req = {
            "type": "set_ready",
            "value": True
        }
        res, msg = table_api.set_readiness(req, self.user1)
        self.assertFalse(res, msg)

    def test_get_readiness_command_fails(self):
        """
        Scenario: Table was build without support for ready command but player invoke get readiness
        Expected outcome: command fails
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        res, msg = table_api.get_player_readiness(self.user1)
        self.assertFalse(res, msg)

    def test_table_setup_transmission(self):
        """
        Scenario: Table was build without support for ready command
        Expected outcome: After both seats are claimed, table enters setup phase
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        super()._run_job_manager(100)
        self.assertIs(table.phase_type, TableGamePhase.setup)

    def test_transmission_to_setup_invokes_board_event_for_all_event_channels(self):
        """
        Scenario: Table transited to 'setup' phase
        Expected behaviour: In all channels there was transmitted board event with
        'game_status' = 'setup'
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        super()._run_job_manager(100)
        for ch in self.event_channels.values():
            events = [arg.args[0] for arg in ch.call_args_list]
            events = [e for e in events if e['type'] == 'board_event'
                      and e['game_status'] == 'setup']
            self.assertTrue(len(events) > 0)

        # check if transmission is recorded by get_board
        self.assertEqual(table_api.get_board(self.user1).get('game_status'), 'setup')


class TestTableAwaitPhaseWithReadyCommand(TestTableAwaitPhase):
    def setUp(self):
        super().setUp()
        self.table_builder.set_use_readiness(True)
        self.table_builder.set_start_timer(50)
        self.set_ready = lambda val: {
            "type": "set_ready",
            "value": val
        }

    def tearDown(self):
        super().tearDown()
        del self.set_ready

    def test_user_set_readiness1(self):
        """
        Scenario: users takes seat and declares readiness
        Expected outcome: commands succeed and ready_event is emitted via event broadcast
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        status, msg = table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(status, msg)
        status, msg = table_api.set_readiness(self.set_ready(True), self.user1)
        self.assertTrue(status, msg)

        ready_events = [args.args[0] for args in self.event_broadcast.call_args_list
                        if args.args[0]['type'] == 'ready_event']
        self.assertEqual(len(ready_events), 1)
        self.assertTrue(ready_events[0]["value"])

    def test_user_set_readiness2(self):
        """
        Scenario: User takes seat, declares readiness and then
        :return:
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        status, msg = table_api.take_seat(self.req_claim_seat('red'), self.user1)
        self.assertTrue(status, msg)
        status, msg = table_api.set_readiness(self.set_ready(True), self.user1)
        self.assertTrue(status, msg)
        status, msg = table_api.set_readiness(self.set_ready(False), self.user1)
        self.assertTrue(status, msg)
        ready_events = [args.args[0] for args in self.event_broadcast.call_args_list
                        if args.args[0]['type'] == 'ready_event']
        self.assertEqual(len(ready_events), 2)
        self.assertTrue(ready_events[0]["value"])
        self.assertFalse(ready_events[1]["value"])

    def test_table_setup_transmission(self):
        """
        Scenario: both players have taken their seats and set their status to ready.
        Expect outcome: table status is  in 'setup' phase.
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        table_api.set_readiness(self.set_ready(True), self.user1)
        table_api.set_readiness(self.set_ready(True), self.user2)
        super()._run_job_manager(100)
        self.assertIs(table.phase_type, TableGamePhase.setup)

    def test_table_setup_transmission2(self):
        """
        Scenario: both players have taken their seats and set their status to ready, then one of players set their
        readiness to false Expect outcome: table status is  in 'setup' phase.
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        table_api.set_readiness(self.set_ready(True), self.user1)
        table_api.set_readiness(self.set_ready(True), self.user2)
        table_api.set_readiness(self.set_ready(False), self.user1)
        super()._run_job_manager(100)
        self.assertIsNot(table.phase_type, TableGamePhase.setup)

    def test_transmission_to_setup_invokes_board_event_for_all_event_channels(self):
        """
        Scenario: Table transited to 'setup' phase
        Expected behaviour: In all channels there was transmitted board event with
        'game_status' = 'setup'
        """
        table = self.table_builder.build()
        table_api = TableApi(table)
        table_api.take_seat(self.req_claim_seat('red'), self.user1)
        table_api.take_seat(self.req_claim_seat('blue'), self.user2)
        table_api.set_readiness(self.set_ready(True), self.user1)
        table_api.set_readiness(self.set_ready(True), self.user2)
        super()._run_job_manager(100)
        for ch in self.event_channels.values():
            events = [arg.args[0] for arg in ch.call_args_list]
            events = [e for e in events if e['type'] == 'board_event'
                      and e['game_status'] == 'setup']
            self.assertTrue(len(events) > 0)

        # check if transmission is recorded by get_board
        self.assertEqual(table_api.get_board(self.user1).get('game_status'), 'setup')


class TestTableSetupPhase(TestTable):
    def setUp(self):
        super().setUp()
        self.table = self.table_builder.set_setup_time(100).build()
        self.table_api = TableApi(self.table)
        req_claim_seat = lambda color: {
            "type": "claim_seat",
            "side": color
        }
        self.table_api.take_seat(req_claim_seat('red'), self.user1)
        self.table_api.take_seat(req_claim_seat('blue'), self.user2)
        while self.table.phase_type is not TableGamePhase.setup:
            self.job_manager.iteration_of_job_execution()

    def tearDown(self):
        super().tearDown()
        del self.table_api
        del self.table

    @staticmethod
    def _send_setup(setup: dict[int, PieceType]):
        return {
            'type': "send_setup",
            'setup': setup_to_protocol_form(setup)
        }

    def _run_fob_manager(self):
        self.job_manager.add_delayed_task(DelayedTask(self.job_manager.kill, 150))
        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()

    def test_time_run_down(self):
        """
         Scenario: players did nothing during this phase
         Expected outcome: Table enters finished state
        """
        self._run_fob_manager()
        self.assertIs(self.table.phase_type, TableGamePhase.finished)

        # check if transmission was recorded in events
        for ch in self.event_channels.values():
            events = [arg.args[0] for arg in ch.call_args_list]
            events = [e for e in events if e['type'] == 'board_event'
                      and e['game_status'] == 'finished']
            self.assertTrue(len(events) > 0)
        # check if transmission is recorded by get_board
        self.assertEqual(self.table_api.get_board(self.user1).get('game_status'), 'finished')

    def test_transmission_to_gameplay(self):
        """
        Scenario: Both players send valid setups for their side
        Expected outcome: Table enters gameplay state
        """
        state = FastWinPosition(Side.red)
        self.table_api.submit_setup(self._send_setup(state.setups[Side.red]), self.user1)
        self.table_api.submit_setup(self._send_setup(state.setups[Side.blue]), self.user2)
        self._run_fob_manager()
        self.assertIs(self.table.phase_type, TableGamePhase.gameplay)

        # check if transmission was recorded in events
        for ch in self.event_channels.values():
            events = [arg.args[0] for arg in ch.call_args_list]
            events = [e for e in events if e['type'] == 'board_event'
                      and e['game_status'] == 'gameplay']
            self.assertTrue(len(events) > 0)

        # check if transmission is recorded by get_board
        self.assertEqual(self.table_api.get_board(self.user1).get('game_status'), 'gameplay')


class TestTableGameplayPhase(TestTable):
    def setUp(self):
        # puts table in a gameplay mode
        super().setUp()
        self.table = self.table_builder.set_setup_time(100).set_time_control(100, 0).build()
        self.table_api = TableApi(self.table)
        req_claim_seat = lambda color: {
            "type": "claim_seat",
            "side": color
        }
        self.table_api.take_seat(req_claim_seat('red'), self.user1)
        self.table_api.take_seat(req_claim_seat('blue'), self.user2)
        while self.table.phase_type is not TableGamePhase.setup:
            self.job_manager.iteration_of_job_execution()

        state = FastWinPosition(Side.red)
        self.table_api.submit_setup(self._send_setup(state.setups[Side.red]), self.user1)
        self.table_api.submit_setup(self._send_setup(state.setups[Side.blue]), self.user2)

        while self.table.phase_type is not TableGamePhase.gameplay:
            self.job_manager.iteration_of_job_execution()

    def tearDown(self):
        super().tearDown()

    @staticmethod
    def _send_setup(setup: dict[int, PieceType]):
        return {
            'type': "send_setup",
            'setup': setup_to_protocol_form(setup)
        }

    def test_red_starts(self):
        """
            Scenario: Board just enter gameplay phase.
            Expected Scenario: Moving side is red

        """
        board = self.table_api.get_board(self.user1)
        self.assertEqual(board.get('moving_side'), 'red')

    def test_player_runs_of_time(self):
        """
            Scenario players time runs out.
            Expected behavior: Table enters the finished state
        """
        self.job_manager.add_delayed_task(DelayedTask(self.job_manager.kill, 500))
        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()
        self.assertEqual(self.table_api.get_board(self.user1).get('game_status'), 'finished')


class TestTableFinishedPhase(TestTable):
    def setUp(self):
        super().setUp()
        self.table = self.table_builder.set_setup_time(20).set_use_readiness(False).build()
        self.table_api = TableApi(self.table)
        req_claim_seat = lambda color: {
            "type": "claim_seat",
            "side": color
        }
        self.set_rematch_willingness = lambda val: {
            'type': "set_rematch_willingness",
            'value': val
        }
        self.table_api.take_seat(req_claim_seat('red'), self.user1)
        self.table_api.take_seat(req_claim_seat('blue'), self.user2)
        while self.table_api.get_board(self.user1).get('game_status') != 'finished':
            self.job_manager.iteration_of_job_execution()

    def tearDown(self):
        del self.table_api, self.table
        super().tearDown()

    def test_players_agreed_to_rematch_causes_transmission_to_awaiting_phase(self):
        s, msg = self.table_api.set_rematch_willingness(self.user1, self.set_rematch_willingness(True))
        self.assertTrue(s, msg)
        s, msg = self.table_api.set_rematch_willingness(self.user2, self.set_rematch_willingness(True))
        self.assertTrue(s, msg)
        self.job_manager.add_delayed_task(DelayedTask(self.job_manager.kill, 200))

        def helper():
            if self.table.phase_type is TableGamePhase.setup:
                self.job_manager.kill()
        self.job_manager.add_job(Job(helper))

        while len(self.job_manager) > 0:
            self.job_manager.iteration_of_job_execution()
        self.assertEqual(self.table.phase_type, TableGamePhase.setup)


class TestTableApi(unittest.TestCase):

    def test_main_loop(self):
        main_loop = MainLoopStub()
        failure_task = DelayedTask(lambda: self.assertEqual(True, False), 4)
        main_loop.get_resource_manager().add_delayed_task(failure_task)
        main_loop.run(3)

    def test_expected_behavior(self):
        main_loop = MainLoopStub()
        event_man = Eventmanager(main_loop.get_resource_manager())
        table = (Table.
                 Builder(main_loop.get_resource_manager()).
                 set_start_timer(100).
                 set_setup_time(300).
                 build())
        usi = UserSimulationInterpreter({"$TableApi": TableApi(table)}, main_loop.get_resource_manager(), event_man)
        player_sim = GameplayScenarioGenerator()
        setup_script = player_sim.assume_random_setup("User1", "User2")
        gameplay_script = player_sim.simulate_gameplay("User1", "User2")
        usi.run_command("WAIT 50")
        try:
            usi.run_script("../TestResources/table_api_test_players_ready")
            check1 = DelayedTask(lambda: self.assertIs(table.phase_type, TableGamePhase.awaiting), usi.now + 20)
            main_loop.get_resource_manager().add_delayed_task(check1)
            usi.run_command("WAIT 120")
            usi.run_command(setup_script)
            check2 = DelayedTask(lambda: self.assertIs(table.phase_type, TableGamePhase.setup), usi.now + 50)
            main_loop.get_resource_manager().add_delayed_task(check2)
            usi.run_command("WAIT 300")
            check3 = DelayedTask(lambda: self.assertIs(table.phase_type, TableGamePhase.gameplay), usi.now + 10)
            main_loop.get_resource_manager().add_delayed_task(check3)
            usi.run_command(gameplay_script)
            check4 = DelayedTask(lambda: self.assertIs(table.phase_type, TableGamePhase.finished), usi.now + 50)
            main_loop.get_resource_manager().add_delayed_task(check4)
            main_loop.run(usi.now + 100)
        except Exception as e:
            print("Test Failed. Saving generating script into a file ...")
            usi.dump("../TestResources/generated_script")
            raise e

    def test_gameplay_timeout(self):
        main_loop = MainLoopStub()
        event_man = Eventmanager(main_loop.get_resource_manager())
        table = (Table.
                 Builder(main_loop.get_resource_manager()).
                 set_start_timer(100).
                 set_setup_time(300).
                 set_time_control(1000, 0).
                 build())
        usi = UserSimulationInterpreter({"$TableApi": TableApi(table)}, main_loop.get_resource_manager(), event_man)
        try:
            usi.run_script("../TestResources/table_api_test_players_ready")
            usi.run_command("WAIT 100")
            usi.run_script("../TestResources/table_api_test_correct_setup")
            usi.run_command("WAIT 300")

            check = DelayedTask(lambda: self.assertIs(table.phase_type, TableGamePhase.finished), usi.now + 1200)
            main_loop.get_resource_manager().add_delayed_task(check)

            main_loop.run(usi.now + 1250)

        except Exception as e:
            print("Test Failed. Saving generating script into aa file ...")
            usi.dump("../TestResources/generated_script")
            raise e

    def test_resign(self):
        main_loop = MainLoopStub()
        event_man = Eventmanager(main_loop.get_resource_manager())
        table = (Table.
                 Builder(main_loop.get_resource_manager()).
                 set_start_timer(100).
                 set_setup_time(300).
                 build())
        usi = UserSimulationInterpreter({"$TableApi": TableApi(table)}, main_loop.get_resource_manager(), event_man)
        usi.run_command("WAIT 50")  # give some time for setting up the test
        try:
            usi.run_script("../TestResources/table_api_test_players_ready")
            usi.run_command("WAIT 100")
            usi.run_script("../TestResources/table_api_test_correct_setup")
            usi.run_command("WAIT 300")
            usi.run_command("User1 resign > {}")
            check = DelayedTask(lambda: self.assertIs(table.phase_type, TableGamePhase.finished), usi.now + 120)
            main_loop.get_resource_manager().add_delayed_task(check)

            main_loop.run(usi.now + 1250)

        except Exception as e:
            print("Test Failed. Saving generating script into aa file ...")
            usi.dump("../TestResources/generated_script")
            raise e


if __name__ == '__main__':
    unittest.main()
