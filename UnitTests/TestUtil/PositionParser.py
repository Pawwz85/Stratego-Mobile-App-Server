"""

"""
from abc import ABC, abstractmethod
from pathlib import Path

from src.Core.stratego_gamestate import GameState, Side, Piece, PieceType


class PositionParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(path: Path) -> GameState:
        pass


class BinaryTestPositionParser(PositionParser):
    #
    #        ----------------------------------------------------
    #        |                   128 Bytes                      |
    #        ----------------------------------------------------
    #        | pos_id | flags |         squares      |  padding |
    #        ----------------------------------------------------
    #        |  4B    |   4B  |         100B         |    20B   |
    #        ----------------------------------------------------
    #        0        4       8                      108       128
    #
    #        Fields pos_id and flags are stored in big endian style
    #
    #        Flags:
    #        Flags & 1 -> True, if side to move is red, otherwise side to move is Blue
    #
    #                                Square:
    #
    #       1       2       4       8       16      32      64      128
    #       BIT0    BIT1    BIT2    BIT3    BIT4    BIT5    BIT6    BIT7
    #       ############################
    #                 type_id             is_red   disc   exist     -
    #
    @staticmethod
    def parse(path: Path) -> GameState:
        with open(path, "rb") as f:
            data = f.read(128)

        mov_side = Side.red if data[7] & 1 else Side.blue
        board = [BinaryTestPositionParser.parse_piece(data[8 + i]) for i in range(100)]
        return GameState(board, mov_side)

    @staticmethod
    def parse_piece(b: int) -> Piece | None:
        side: Side = Side.red if b & 16 else Side.blue
        disc: bool = b & 32 != 0
        exist: bool = b & 64 != 0

        piece_type_dict = {
            0: PieceType.flag,
            1: PieceType.mine,
            2: PieceType.spy,
            3: PieceType.scout,
            4: PieceType.miner,
            5: PieceType.sergeant,
            6: PieceType.lieutenant,
            7: PieceType.captain,
            8: PieceType.major,
            9: PieceType.colonel,
            10: PieceType.general,
            11: PieceType.marshal
        }
        piece_type = piece_type_dict.get(b & 15)

        if not exist or piece_type is None:
            return None
        else:
            p = Piece(side, piece_type)
            p.discovered = disc
            return p
