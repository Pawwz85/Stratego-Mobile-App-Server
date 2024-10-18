import time
import unittest
from collections import deque
from UnitTests.TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator
from src.Core.GameInstanceFactory import GameInstanceFactory
from src.Core.stratego_gamestate import Piece
import cProfile, pstats, io
from pstats import SortKey


class MoveGenPerf(unittest.TestCase):

    def test_cmove_gen(self, games=100):
        cnt = 0
        start = time.time()
        for _ in range(games):
            for gs in GameplayScenarioGenerator().create_match(GameInstanceFactory().create_c_game_instance()):
                gs.move_gen(gs.get_side())
                cnt = cnt + 1

        pos_per_sec = cnt/(time.time() - start)
        print(f"C implementation: {pos_per_sec} positions per second")

    def test_pythonmove_gen(self, games=100):
        cnt = 0
        start = time.time()
        for _ in range(games):
            for gs in GameplayScenarioGenerator().create_match(GameInstanceFactory().create_pure_python_game_instance()):
                gs.move_gen(gs.get_side())
                cnt = cnt + 1

        pos_per_sec = cnt/(time.time() - start)
        print(f"Python implementation: {pos_per_sec} positions per second")


if __name__ == '__main__':
    unittest.main()
