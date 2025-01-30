import random
import unittest

import src.Core.stratego as stratego
import src.Core.stratego_gamestate
from UnitTests.TestUtil.GameplayScenarioGenerator import GameplayScenarioGenerator

"""
    This file checks a bunch of features in stratego.py
"""


class StrategoUtilsTest(unittest.TestCase):
    def testFlip(self):
        self.assertIs(src.Core.stratego_gamestate.Side.red, src.Core.stratego_gamestate.Side.blue.flip())
        self.assertIs(src.Core.stratego_gamestate.Side.blue, src.Core.stratego_gamestate.Side.red.flip())

    def testWhoWouldWinTest(self):
        fight = lambda type1, type2: stratego._who_wins(
            src.Core.stratego_gamestate.Piece(src.Core.stratego_gamestate.Side.red, type1),
            src.Core.stratego_gamestate.Piece(src.Core.stratego_gamestate.Side.blue,
                                              type2) if type2 is not None else None)
        get_type = lambda p: p if p is None else p.type
        foo = lambda type1, type2: get_type(fight(type1, type2))

        for type in src.Core.stratego_gamestate.PieceType:
            self.assertIs(foo(type, type), None)
            self.assertIs(foo(type, None), type)
            if type in src.Core.stratego_gamestate._mobile_set and type is not src.Core.stratego_gamestate.PieceType.miner:
                self.assertIs(foo(type, src.Core.stratego_gamestate.PieceType.mine), src.Core.stratego_gamestate.PieceType.mine)
            if type in src.Core.stratego_gamestate._mobile_set:
                self.assertIs(foo(type, src.Core.stratego_gamestate.PieceType.flag), type)

        self.assertIs(foo(src.Core.stratego_gamestate.PieceType.miner, src.Core.stratego_gamestate.PieceType.mine), src.Core.stratego_gamestate.PieceType.miner)
        self.assertIs(foo(src.Core.stratego_gamestate.PieceType.marshal, src.Core.stratego_gamestate.PieceType.spy), src.Core.stratego_gamestate.PieceType.marshal)
        self.assertIs(foo(src.Core.stratego_gamestate.PieceType.spy, src.Core.stratego_gamestate.PieceType.marshal), src.Core.stratego_gamestate.PieceType.spy)

    @staticmethod
    def generate_random_setup(side: src.Core.stratego_gamestate.Side) -> dict[int, src.Core.stratego_gamestate.PieceType]:
        setup = {}
        piece_counts = src.Core.stratego_gamestate._piece_type_setup_count.copy()
        available_squares = list(range(60, 100)) if side == src.Core.stratego_gamestate.Side.red else list(range(40))
        random.shuffle(available_squares)

        for piece_type, count in piece_counts.items():
            for _ in range(count):
                square = available_squares.pop()
                setup[square] = piece_type

        return setup

    def testVerifySetupDict(self):
        for i in range(100):
            for side in src.Core.stratego_gamestate.Side:
                self.assertIs(src.Core.stratego_gamestate.verify_setup_dict(
                    self.generate_random_setup(side), side
                ), True)

                # edge case 1: empty dict
                self.assertIs(src.Core.stratego_gamestate.verify_setup_dict(dict(), side), False)

                # edge case 2: correct placement, incorrect unit's type
                range_ = range(40) if side is src.Core.stratego_gamestate.Side.blue else range(60, 100)
                self.assertIs(src.Core.stratego_gamestate.verify_setup_dict({sq_id: src.Core.stratego_gamestate.PieceType.flag
                                                                             for sq_id in range_}, side),
                              False)

                # edge case 3: correct units composition, incorrect placement
                self.assertIs(src.Core.stratego_gamestate.verify_setup_dict(
                    self.generate_random_setup(side), side.flip()), False)

    def testStateFromSetups(self):
        list_to_dict = lambda list_: {i: list_[i] for i in range(len(list_)) if list_[i] is not None}
        filter_ = lambda dict_, color: {i: item for i, item in dict_.items() if item.color is color}
        map_ = lambda dict_: {key: value.type for key, value in dict_.items()}
        retrieve_setup = lambda setup, color: map_(filter_(list_to_dict(setup.get_board()), color))
        contains_ = lambda dict_, dict_2: \
            len(dict_) == len({key for key in dict_.keys() if dict_.get(key) == dict_2.get(key)})
        dict_eqs = lambda dict_, dict_2: contains_(dict_, dict_2) and contains_(dict_2, dict_)

        # test lambdas
        self.assertTrue(dict_eqs({1: 2, 2: 3}, {2: 3, 1: 2}))
        self.assertFalse(dict_eqs({1: 2, 2: 3}, {1: 2, 2: 3, 3: 4}))

        for _ in range(100):
            red_setup = self.generate_random_setup(src.Core.stratego_gamestate.Side.red)
            blue_setup = self.generate_random_setup(src.Core.stratego_gamestate.Side.blue)
            state = src.Core.stratego_gamestate.game_state_from_setups(red_setup, blue_setup)
            self.assertTrue(dict_eqs(red_setup, retrieve_setup(state, src.Core.stratego_gamestate.Side.red)))
            self.assertTrue(dict_eqs(blue_setup, retrieve_setup(state, src.Core.stratego_gamestate.Side.blue)))


class StrategoGameStateTest(unittest.TestCase):

    def testTrackers(self):
        generator = GameplayScenarioGenerator()
        to_type = lambda p: None if p is None else p.type
        pred = lambda p, color: to_type(p) in src.Core.stratego_gamestate._mobile_set and p.color is color
        count_movable = lambda color: len([p for p in state.get_board() if pred(p, color)])

        for _ in range(100):
            state = stratego.PurePythonGameInstance()
            state.set_game_state(
                src.Core.stratego_gamestate.game_state_from_setups(StrategoUtilsTest.generate_random_setup(
                    src.Core.stratego_gamestate.Side.red),
                                                StrategoUtilsTest.generate_random_setup(
                                                    src.Core.stratego_gamestate.Side.blue)))

            while not state.is_game_finish():
                for side in src.Core.stratego_gamestate.Side:
                    self.assertEqual(state._mobile_tracker[side], count_movable(side))
                move = generator.ai(state, state.get_side())
                state.execute_move(move)


if __name__ == '__main__':
    unittest.main()
