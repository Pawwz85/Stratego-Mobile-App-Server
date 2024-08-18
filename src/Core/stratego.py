import json
from collections import deque
from enum import Enum

"""
    Straight forward Stratego implementation.
"""
_lake_set = {42, 43, 46, 47, 52, 53, 56, 57}


class PieceType(Enum):
    flag = 0
    spy = 1
    scout = 2
    miner = 3
    sergeant = 4
    lieutenant = 5
    captain = 6
    major = 7
    colonel = 8
    general = 9
    marshal = 10
    mine = 100


_piece_type_setup_count: dict[PieceType, int] = {
    PieceType.flag: 1,
    PieceType.spy: 1,
    PieceType.scout: 8,
    PieceType.miner: 5,
    PieceType.sergeant: 4,
    PieceType.lieutenant: 4,
    PieceType.captain: 4,
    PieceType.major: 3,
    PieceType.colonel: 2,
    PieceType.general: 1,
    PieceType.marshal: 1,
    PieceType.mine: 6
}

_immobile_set = {PieceType.flag, PieceType.mine}
_mobile_set = {piece_type for piece_type in PieceType if piece_type not in _immobile_set}


class Side(Enum):
    red = False
    blue = True

    def flip(self):
        return Side.red if self.value else Side.blue


class Piece:
    """
        Represents a single piece on the board.
    """

    def __init__(self, color: Side, piece_type: PieceType):
        self.color = color
        self.type = piece_type
        self.discovered = False

    def to_json(self):
        return {
            "color": "red" if self.color is Side.red else "blue",
            "type": _piece_type_to_str[self.type],
            "discovered": self.discovered
        }


def _who_wins(attacker: Piece, defender: Piece | None) -> Piece | None:
    """
    Function to determine who wins in an attack
    :param attacker: Attacking Piece
    :param defender: Defending Piece
    :return:
    """
    if defender is None:
        return attacker

    # Special rules Spy vs Marshal, Miner vs Mine
    if attacker.type is PieceType.spy and defender.type is PieceType.marshal:
        return attacker

    # Compare piece types to determine winner

    if attacker.type is PieceType.miner and defender.type is PieceType.mine:
        return attacker

    if attacker.type.value > defender.type.value:
        return attacker

    if attacker.type.value < defender.type.value:
        return defender

    # if attacker value eq defender value, there is no winner
    return None


class GameStateViewToken:
    """
        This class is meant to represent a singular piece in player view.
        In that system pieces can be "Unknown", or have a defined value.
        Possible "type" values:
        "?" - Unknown,
        "F" - Flag,
        "B" - bomb/mine,
        "S" - Spy,
        from "2" to "10" - rest of army
    """

    def __init__(self, symbol: str, side: Side):
        self.type: str = symbol
        self.side: Side = side

    def to_json(self):
        return {"side": "red" if self.side is Side.red else "blue",
                "type": self.type}


_piece_type_to_str: dict[PieceType, str] = {
    PieceType.flag: "F",
    PieceType.spy: "S",
    PieceType.scout: "2",
    PieceType.miner: "3",
    PieceType.sergeant: "4",
    PieceType.lieutenant: "5",
    PieceType.captain: "6",
    PieceType.major: "7",
    PieceType.colonel: "8",
    PieceType.general: "9",
    PieceType.marshal: "10",
    PieceType.mine: "B"
}


class GameStateView:
    """
    This class is designed to represent how given player should see the board.
    Ideally, stratego we would want to expose this class to the client, instead of raw board game state.
    Doing so we could prevent some clients from "peeking" on their opponents
    """

    def __init__(self, view: list[GameStateViewToken | None]):
        self._view = view

    def get_view(self):
        return self._view

    def __getitem__(self, item):
        return self._view[item]

class GameState:
    def __init__(self):
        self._board: list[None | Piece] = [None] * 100
        self._side_to_move: Side = Side.red
        self._mobile_tracker = {Side.red: 0, Side.blue: 0}
        self._flag_captured = {Side.red: False, Side.blue: False}

    def __getitem__(self, item: int):
        if item < 0 or item >= 100:
            return None
        return self._board[item]

    def get_side(self):
        return self._side_to_move

    @staticmethod
    def __sign(x: int) -> int:
        return 0 if x == 0 else (1 if x > 0 else -1)

    def _is_scout_move_legal(self, _from, _to, side) -> bool:
        x1, y1 = self.to_cords(_from)
        x2, y2 = self.to_cords(_to)
        if x1 != x2 and y1 != y2:
            return False

        dx, dy = x2 - x1, y2 - y1
        dx = GameState.__sign(dx)
        dy = GameState.__sign(dy)
        d = dx + 10 * dy

        sq = _from
        while sq != _to:
            sq += d
            if sq in _lake_set:
                return False
            if self._board[sq] is not None:
                return self._board[sq].color is not side and sq == _to

        return True

    @staticmethod
    def to_cords(sq_id: int) -> tuple[int, int]:
        return sq_id % 10, sq_id // 10

    def is_move_legal(self, move: tuple[int, int]) -> bool:
        _from, _to = move
        piece = self[_from]
        if piece is None or piece.color is not self._side_to_move or _to not in range(100) or _to in _lake_set:
            return False

        if piece.type in _immobile_set:
            return False

        if piece.type is PieceType.scout:
            return self._is_scout_move_legal(_from, _to, piece.color)

        # Check if move sq from and sq to are adjacent
        x1, y1 = self.to_cords(_from)
        x2, y2 = self.to_cords(_to)
        if abs(x1 - x2) + abs(y2 - y1) != 1:
            return False

        enemy_piece = self[_to]
        return enemy_piece is None or enemy_piece.color is not piece.color

    def _clear_sq(self, sq: int):
        """
        method to remove a piece from given sq while preserving validity of trackers
        :param sq: Sq to clear
        :return:
        """
        piece = self[sq]
        if piece is not None:
            self._board[sq] = None
            if piece.type in _mobile_set:
                self._mobile_tracker[piece.color] -= 1

            if piece.type is PieceType.flag:
                self._flag_captured[piece.color] = True

    def _spawn_piece_on_sq(self, sq: int, piece: Piece | None):
        """
        A method to spawn a piece on given sq while preserving validity of trackers
        :param sq:
        :param piece:
        :return:
        """
        self._board[sq] = piece
        if piece is not None:
            if piece.type in _mobile_set:
                self._mobile_tracker[piece.color] += 1

            if piece.type is PieceType.flag:
                self._flag_captured[piece.color] = False

    def execute_move(self, move: tuple[int, int]):
        _from, _to = move
        moved_piece = self[_from]
        attacked_piece = self[_to]

        victorious_piece = _who_wins(moved_piece, attacked_piece)
        if victorious_piece is not None and attacked_piece is not None:
            victorious_piece.discovered = True

        self._clear_sq(_from)
        self._clear_sq(_to)
        self._spawn_piece_on_sq(_to, victorious_piece)
        self._side_to_move = self._side_to_move.flip()

    def is_game_finish(self):
        for side in Side:
            if self._mobile_tracker[side] == 0 or self._flag_captured[side]:
                return True
        return False

    def get_winner(self) -> Side | None:
        for side in Side:
            if self._mobile_tracker[side] == 0 or self._flag_captured[side]:
                return side.flip()
        return None

    def set_game_state(self, new_game_state: list[Piece]):
        for i in range(100):
            self._clear_sq(i)
            self._spawn_piece_on_sq(i, new_game_state[i])

    def get_game_state(self):
        return self._board.copy()

    def move_gen(self, side: Side):
        pseudo_legal_moves: deque[tuple[int, int]] = deque()
        for i, p in enumerate(self._board):
            if p is not None and p.color is side:
                if p.type is PieceType.scout:
                    x, y = self.to_cords(i)
                    pseudo_legal_moves += [(i, x + 10 * j) for j in range(10) if j != y]
                    pseudo_legal_moves += [(i, j + 10 * y) for j in range(10) if j != x]
                else:
                    pseudo_legal_moves += [(i, i + d) for d in [-10, -1, 1, 10]]

        return [m for m in pseudo_legal_moves if self.is_move_legal(m)]

    @staticmethod
    def __generate_token(piece: Piece | None, viewer_side: Side | None) -> GameStateViewToken | None:
        """
        Generates a token object (representing a piece or an unknown value) to be displayed in the game view based on
        the given piece and the viewing side's color. If the piece is None or the viewing side's color does not
        match, returns `None`, otherwise returns either `"?"` (if the piece has not been discovered yet) or a string
        representing the type of the piece.
        """
        if piece is None:
            return piece

        if viewer_side is not piece.color and not piece.discovered:
            return GameStateViewToken("?", piece.color)

        return GameStateViewToken(_piece_type_to_str[piece.type], piece.color)

    def get_view(self, side: Side | None) -> GameStateView:
        """
        Returns a view object containing all the pieces in the game state, with their corresponding token objects
        based on the viewing side's color (as generated by `__generate_token()`). This method is used to display the
        game state to the player.
        """
        result = [self.__generate_token(piece, side) for piece in self._board]
        return GameStateView(result)


def verify_setup_dict(setup: dict[int, PieceType], side: Side) -> bool:
    """
    This functions simply checks if given dictionary is correct setup according to project documentation:
    1. All pieces are placed in territory allowed for this side to set up
    2. Each PieceType is present in dictionary precisely the amount of times specified in documentation
    for given piece type.

    :param setup: A python dictionary that maps square ids to PieceType.
    :param side: Side for which we are checking correctness
    :return: True if setup is valid, false otherwise
    """

    # We don't actually need this check
    # if len(setup) != 40:
    #    return False

    allowed_area = range(60, 100) if side.value else range(0, 40)

    for key in setup.keys():
        if key not in allowed_area:
            return False

    temp_dict = {piece_type: 0 for piece_type in PieceType}

    for v in setup.values():
        temp_dict[v] += 1

    for piece_type in PieceType:
        if temp_dict[piece_type] != _piece_type_setup_count[piece_type]:
            return False

    return True


def game_state_from_setups(red_setup: dict[int, PieceType], blue_setup: dict[int, PieceType]) -> list[Piece | None]:
    """
    This function simply generates a valid input for GameState.set_game_state() method.
    """
    result: list[Piece | None] = [None] * 100

    for key in red_setup.keys():
        result[key] = Piece(Side.red, red_setup[key])

    for key in blue_setup.keys():
        result[key] = Piece(Side.blue, blue_setup[key])

    return result
