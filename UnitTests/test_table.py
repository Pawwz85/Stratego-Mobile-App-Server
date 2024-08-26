import random
import unittest
import unittest.mock as mock
from TestUtil.MainLoopStub import MainLoopStub
from TestUtil.UserSimulation import UserSimulationInterpreter
from TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator
from UnitTests.TestUtil.random_setup import generate_random_setup
from src.Core.table import *
from src.Core.table import (TablePhase, SeatManager, SetupManager, GameplayManager,
                            SeatManagerWithReadyCommand, FinishedStateManager)
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
        testcases = [{Side.red: None, Side.blue: None}, {Side.red: None, Side.blue: 1}, {Side.red: 2, Side.blue: None}, {Side.red: 2, Side.blue: 1}]
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

    def test_phase_finish_top_transmission(self):
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
