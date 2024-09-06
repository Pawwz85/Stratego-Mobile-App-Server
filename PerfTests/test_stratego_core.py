import time
import unittest
from collections import deque
from UnitTests.TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator
from src.Core.stratego_gamestate import Piece
import cProfile, pstats, io
from pstats import SortKey

class MoveGenPerf(unittest.TestCase):

    def test_move_gen(self, games=10):
        #pr = cProfile.Profile()
        #pr.enable()
        cnt = 0
        start = time.time()
        for _ in range(games):
            for gs in GameplayScenarioGenerator().create_match():
                gs.move_gen(gs.get_side())
                cnt = cnt + 1

        pos_per_sec = cnt/(time.time() - start)
        #pr.disable()
        #s = io.StringIO()
        #sortby = SortKey.TIME
        #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        #ps.print_stats()
        #print(s.getvalue())
        print(pos_per_sec)


if __name__ == '__main__':
    unittest.main()
