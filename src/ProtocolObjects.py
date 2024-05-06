"""
    This file contains classes that
"""
from __future__ import annotations

from src.stratego import PieceType, _piece_type_to_str


class ParsingException(Exception):
    pass


class PieceToken:
    __token_to_piece_type = {v: k for k, v in _piece_type_to_str.items()}

    def __init__(self, sq: int, token: str):
        self.sq = sq
        self.piece = token

    def get_piece_type(self) -> PieceType:
        return PieceToken.__token_to_piece_type[self.piece]

    @staticmethod
    def parse_from_dict(x: dict[str, any]) -> PieceToken:

        square = x.get("sq")
        tok = x.get("piece")

        if type(square) is not int:
            raise ParsingException()

        if tok not in _piece_type_to_str.values():
            raise ParsingException()

        return PieceToken(square, tok)

    def to_dict(self):
        return {"sq": self.sq, "piece": self.piece}


class Move:
    def __init__(self, from_: int, to_: int):
        self.from_ = from_
        self.to_ = to_

    @staticmethod
    def parse_from_dict(x: dict[str, any]) -> Move:
        from_ = x.get("from")
        to_ = x.get("to")
        if type(from_) is not int or type(to_) is not int:
            raise ParsingException()
        return Move(from_, to_)
