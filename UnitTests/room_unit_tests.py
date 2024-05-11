import unittest

from UnitTests.TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator
from UnitTests.TestUtil.MainLoopStub import MainLoopStub
from UnitTests.TestUtil.UserSimulation import UserSimulationInterpreter, convert_script
from UnitTests.TestUtil.EventManagerWithTracking import EvenManagerWithTracking as Eventmanager
from src.Core.Room import Room, RoomApi
from src.Core.table import Table


class MyTestCase(unittest.TestCase):
    table_api_to_room_api_mapping = {
        "take_seat": "claim_seat",
        "submit_setup": "send_setup",
        "make_move": "make_move",
        "resign": "resign",
        "leave_table": "leave_table",
        "set_readiness": "set_readiness",
        "release_seat": "release_seat",
        "get_board": "get_board",
        "set_rematch_willingness": "set_rematch_willingness"
    }

    def test_expected_behaviour(self):
        main_loop = MainLoopStub()
        event_man = Eventmanager(main_loop.get_resource_manager())
        room = Room.Builder(main_loop.get_resource_manager(), lambda x: None).set_table_builder(
            Table.Builder(main_loop.get_resource_manager()).
            set_start_timer(100).
            set_setup_time(300)
        ).build()
        gameplay_scenario_gen = GameplayScenarioGenerator()
        setup_script = gameplay_scenario_gen.assume_random_setup("User1", "User2")
        setup_script = convert_script(setup_script, "$RoomApi", MyTestCase.table_api_to_room_api_mapping)
        gameplay_script = gameplay_scenario_gen.simulate_gameplay("User1", "User2")
        gameplay_script = convert_script(gameplay_script, "$RoomApi", MyTestCase.table_api_to_room_api_mapping)
        usi = UserSimulationInterpreter({"$RoomApi": RoomApi(room)}, main_loop.get_resource_manager(), event_man)
        try:
            usi.run_command("$RoomApi\nUser1 join > {}\nWAIT 20\nUser2 join > {}\nWAIT 20")
            usi.run_script("../TestResources/table_api_test_players_ready", "$RoomApi", MyTestCase.table_api_to_room_api_mapping)
            usi.run_command("WAIT 110")
            usi.run_command(setup_script)
            usi.run_command("WAIT 310")
            usi.run_command(gameplay_script)
            usi.run_command("WAIT 20")

            setup_script = gameplay_scenario_gen.assume_random_setup("User2", "User1")
            setup_script = convert_script(setup_script, "$RoomApi", MyTestCase.table_api_to_room_api_mapping)
            gameplay_script = gameplay_scenario_gen.simulate_gameplay("User2", "User1")
            gameplay_script = convert_script(gameplay_script, "$RoomApi", MyTestCase.table_api_to_room_api_mapping)

            usi.run_command('User1 set_rematch_willingness > {"value":true}')
            usi.run_command('User2 set_rematch_willingness > {"value":true}')
            usi.run_command("WAIT 50")
            usi.run_command(setup_script)
            usi.run_command("WAIT 300")
            usi.run_command(gameplay_script)

            usi.run_command("WAIT 50")
            usi.run_command("User1 release_seat > {}")

            main_loop.run(usi.now + 1250)

        except Exception as e:
            print("Test Failed. Saving generating script into aa file ...")
            usi.dump("../TestResources/generated_script")
            raise e


if __name__ == '__main__':
        unittest.main()

