from pathlib import Path
import unittest

from UnitTests.TestUtil.PositionParser import BinaryTestPositionParser
from src.Core.stratego import GameInstance
from src.Core.stratego_gamestate import GameState, Side
from src.ProtocolObjects import Move


class TestMoveGen(unittest.TestCase):

    @staticmethod
    def sort_move_list(move_list: list[tuple[int, int]]):
        move_list.sort(key=lambda m: m[0] * 100 + m[1])

    @staticmethod
    def fast_move_composer(from_: int, to_: list[int]) -> list[tuple[int, int]]:
        return [(from_, sq) for sq in to_]

    @staticmethod
    def comp_m_list(move_list1: list[tuple[int, int]], move_list2: list[tuple[int, int]]) -> bool:
        TestMoveGen.sort_move_list(move_list1)
        TestMoveGen.sort_move_list(move_list2)
        print("Move list 1", move_list1)
        print("Move list 2", move_list2)
        if len(move_list1) != len(move_list2):
            return False

        for i in range(len(move_list1)):
            m1 = move_list1[i]
            m2 = move_list2[i]
            if m1[0] != m2[0] or m1[1] != m2[1]:
                return False
        return True

    def setUp(self):
        self.game_state: GameState = GameState([None] * 100, Side.red)
        self.game_instance = GameInstance()

    def tearDown(self):
        del self.game_state, self.game_instance

    def load_position(self, path: str):
        path: Path = Path(path)
        self.game_state = BinaryTestPositionParser.parse(path)
        self.game_instance.set_game_state(self.game_state)

    def test_pos000(self):
        self.load_position("../TestResources/TestPositions/pos000.pos")
        scout_m = [90, 81, 82, 83, 84, 85, 86, 87, 88, 89, 70, 60, 50, 40, 30, 20, 10, 0]
        expected_moves = self.fast_move_composer(80, scout_m)
        generated_moves = self.game_instance.move_gen(self.game_state.get_side_to_move())
        self.assertTrue(self.comp_m_list(expected_moves, generated_moves))
        self.assertFalse(self.game_instance.is_game_finish())

    def test_pos001(self):
        self.load_position("../TestResources/TestPositions/pos001.pos")
        spy_m = [1, 3, 12]
        expected_moves = self.fast_move_composer(2, spy_m)
        generated_moves = self.game_instance.move_gen(self.game_state.get_side_to_move())
        self.assertTrue(self.comp_m_list(expected_moves, generated_moves))
        self.assertFalse(self.game_instance.is_game_finish())

    def test_pos002(self):
        self.load_position("../TestResources/TestPositions/pos002.pos")
        generated_moves = self.game_instance.move_gen(self.game_state.get_side_to_move())
        self.assertTrue(self.comp_m_list([], generated_moves))
        self.assertTrue(self.game_instance.is_game_finish())

    def test_pos003(self):
        self.load_position("../TestResources/TestPositions/pos003.pos")
        generated_moves = self.game_instance.move_gen(self.game_state.get_side_to_move())
        scout_m = self.fast_move_composer(54, [24, 34, 44, 55, 64, 74, 84, 94])
        miner_m = self.fast_move_composer(49, [39, 48, 59])
        expected_moves = scout_m + miner_m
        self.assertTrue(self.comp_m_list(expected_moves, generated_moves))
        self.assertFalse(self.game_instance.is_game_finish())

    def test_pos004(self):
        self.load_position("../TestResources/TestPositions/pos004.pos")
        generated_moves = self.game_instance.move_gen(self.game_state.get_side_to_move())
        miner1_m = self.fast_move_composer(44, [34])
        miner2_m = self.fast_move_composer(45, [35])
        miner3_m = self.fast_move_composer(54, [64])
        scout_m  = self.fast_move_composer(55, [65, 75, 85, 95])
        expected_moves = miner1_m + miner2_m + miner3_m + scout_m
        self.assertTrue(self.comp_m_list(expected_moves, generated_moves))
        self.assertFalse(self.game_instance.is_game_finish())
