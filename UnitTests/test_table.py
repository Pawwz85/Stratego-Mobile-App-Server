import unittest
from TestUtil.MainLoopStub import MainLoopStub
from TestUtil.UserSimulation import UserSimulationInterpreter
from TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator
from src.Core.table import *
from src.Events.Events import Eventmanager


class TableTestCase(unittest.TestCase):

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
