from __future__ import annotations

import ctypes
import os.path
import platform

from src.Core.singleton import singleton
from src.Core.stratego import GameInstance
from src.Core.stratego_gamestate import Side, Piece, PieceType, GameState


class OSNotSupported(BaseException):
    pass


class CStrategoApiException(BaseException):
    pass


def load_cstratego_dll(path: str):
    print(f"System: {platform.system()}")
    if platform.system() == "Windows":
        full_path = f"{path}.dll"
    elif platform.system() == "Linux":
        full_path = f"{path}.so"
    else:
        raise OSNotSupported
    print(os.path.abspath(full_path))
    lib = ctypes.CDLL(os.path.abspath(full_path))
    lib.game_state_alloc.restype = ctypes.c_void_p
    lib.game_state_dealloc.argtypes = [ctypes.c_void_p]
    lib.game_state_dealloc.restype = None

    lib.game_state_get_side_to_move.restype = ctypes.c_int
    lib.game_state_get_side_to_move.argtypes = [ctypes.c_void_p]

    lib.game_state_is_move_legal.restype = ctypes.c_int
    lib.game_state_is_move_legal.argtypes = [ctypes.c_void_p, ctypes.POINTER(CStrategoMove)]

    lib.game_state_make_move.restype = None
    lib.game_state_make_move.argtypes = [ctypes.c_void_p, ctypes.POINTER(CStrategoMove)]

    lib.game_state_set_state.restype = ctypes.c_int
    lib.game_state_set_state.argtypes = [ctypes.c_void_p, ctypes.POINTER(CStrategoPiece), ctypes.c_int]

    lib.game_state_get_piece.restype = ctypes.POINTER(CStrategoPiece)
    lib.game_state_get_piece.argtypes = [ctypes.c_void_p, ctypes.c_uint]

    lib.game_state_get_move_buffer.restype = ctypes.POINTER(CStrategoMove)
    lib.game_state_get_move_buffer.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint)]

    lib.get_winner.restype = ctypes.c_int
    lib.get_winner.argtypes = [ctypes.c_void_p]

    lib.init.restype = None
    lib.init.argtypes = []

    lib.init()  # call init of a dll

    return lib


@singleton
class CStrategoMoveGenLibrary:
    def __init__(self):
        try:
            self.cstrategodll = load_cstratego_dll("../dll/StrategoMoveGenerator")
        except OSNotSupported:
            self.cstrategodll = None
        except FileNotFoundError:
            self.cstrategodll = None

    @staticmethod
    def get_instance() -> CStrategoMoveGenLibrary:
        # This method will be created by @singleton decorator
        pass


class CStrategoMove(ctypes.Structure):
    _fields_ = [
        ("from_", ctypes.c_ubyte),
        ("to_", ctypes.c_ubyte)
    ]


class CStrategoPiece(ctypes.Structure):
    _fields_ = [
        ("piece_type", ctypes.c_int),
        ("discovered", ctypes.c_int),
        ("color",      ctypes.c_int),
        ("exist",      ctypes.c_int)
    ]

    type_dict = {
            0: PieceType.flag,
            1: PieceType.spy,
            2: PieceType.scout,
            3: PieceType.miner,
            4: PieceType.sergeant,
            5: PieceType.lieutenant,
            6: PieceType.captain,
            7: PieceType.major,
            8: PieceType.colonel,
            9: PieceType.general,
            10: PieceType.marshal,
            11: PieceType.mine
        }

    rev_type_dict = {
        item: key for key, item in type_dict.items()
    }


def c_stratego_piece_to_piece(piece: CStrategoPiece) -> Piece | None:
    if piece.exist == 0:
        return None
    side = Side.blue if piece.color == 0 else Side.red
    type_: PieceType = piece.type_dict.get(piece.piece_type, PieceType.sergeant)
    result = Piece(side, type_)
    result.discovered = piece.discovered != 0
    return result


def piece_to_c_stratego_piece(piece: Piece | None) -> CStrategoPiece:
    result = CStrategoPiece()
    if piece is None:
        result.exist = 0
        return result

    result.piece_type = CStrategoPiece.rev_type_dict.get(piece.type, 4)
    result.exist = 1
    result.discovered = 1 if piece.discovered else 0
    result.color = 1 if piece.color is Side.red else 0
    return result


class CStrategoGameState(GameInstance):

    def __init__(self, lib: ctypes.cdll):
        self.__lib = lib
        self.__handle: ctypes.c_void_p = self.__lib.game_state_alloc()

    def __del__(self):
        self.__lib.game_state_dealloc(self.__handle)

    @staticmethod
    def __parse_side(c_side: ctypes.c_int):
        return {0: None, 1: Side.red, 2: Side.blue}.get(c_side, None)

    def move_gen(self, side: Side) -> list[tuple[int, int]]:
        if self.__parse_side(self.__lib.game_state_get_side_to_move(self.__handle)) is not side:
            return []

        pointer = ctypes.POINTER(ctypes.c_uint)
        size: ctypes.c_uint = ctypes.c_uint()
        ptr = pointer(size)
        move_buff: ctypes.POINTER(CStrategoMove) \
            = self.__lib.game_state_get_move_buffer(self.__handle, ctypes.byref(size))

        return [(move_buff[i].from_, move_buff[i].to_) for i in range(size.value)]

    def __getitem__(self, item: int):
        if item < 0 or item >= 100:
            return None

        piece: ctypes.POINTER(CStrategoPiece) = self.__lib.game_state_get_piece(self.__handle, ctypes.c_uint(item))
        return c_stratego_piece_to_piece(piece.contents)

    def get_board(self) -> list[Piece | None]:
        return [self[i] for i in range(100)]

    def get_side(self) -> Side:
        side = self.__lib.game_state_get_side_to_move(self.__handle)
        result = self.__parse_side(side)
        return result if result is not None else Side.red

    def execute_move(self, move: tuple[int, int]):
        cmove = CStrategoMove()
        from_, to_ = move
        cmove.from_ = from_
        cmove.to_ = to_
        self.__lib.game_state_make_move(self.__handle, ctypes.byref(cmove))

    def is_move_legal(self, move: tuple[int, int]) -> bool:
        cmove = CStrategoMove()
        from_, to_ = move
        cmove.from_ = from_
        cmove.to_ = to_
        result: ctypes.c_int = self.__lib.game_state_is_move_legal(self.__handle, ctypes.byref(cmove))
        return result > 0

    def is_game_finish(self):
        return self.get_winner() is not None

    def get_winner(self) -> Side | None:
        winner: ctypes.c_int = self.__lib.get_winner(self.__handle)
        return self.__parse_side(winner)

    def set_game_state(self, new_game_state: GameState):
        side = ctypes.c_int(1 if new_game_state.get_side_to_move() is Side.red else 2)
        seq = (CStrategoPiece * 100)(*(piece_to_c_stratego_piece(p) for p in new_game_state.get_board()))
        arr = ctypes.cast(seq, ctypes.POINTER(CStrategoPiece))

        res = self.__lib.game_state_set_state(self.__handle, arr, side)
        if not res:
            raise CStrategoApiException

