"""
    Those tests test behaviour of the ported c
"""
import unittest

import src.Core.cstratego as cstratego
from src.Core.stratego_gamestate import PieceType, Side, Piece


class CStrategoPieceTest(unittest.TestCase):

    def setUp(self):
        self.examples = []
        for tp in PieceType:
            for color in Side:
                self.examples.append(Piece(color, tp))

    def tearDown(self):
        del self.examples

    def test_conversion(self):
        for ex in self.examples:
            cpiece = cstratego.piece_to_c_stratego_piece(ex)
            piece2 = cstratego.c_stratego_piece_to_piece(cpiece)

            self.assertIs(ex.type, piece2.type)
            self.assertIs(ex.color, piece2.color)
            self.assertEqual(ex.discovered, piece2.discovered)

    def test_None(self):
        cpiece = cstratego.piece_to_c_stratego_piece(None)
        piece = cstratego.c_stratego_piece_to_piece(cpiece)
        self.assertIs(None, piece)