from collections import deque

from src.Core.stratego_gamestate import PieceType, _lake_set, _immobile_set, _mobile_set, Side, \
    Piece, _piece_type_to_str, GameStateViewToken, GameStateView, GameState

"""
    Straight forward Stratego implementation.
"""


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


class GameInstance:
    """
        The main
    """
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
        dx = GameInstance.__sign(dx)
        dy = GameInstance.__sign(dy)
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

    def set_game_state(self, new_game_state: GameState):
        board = new_game_state.get_board()
        self._side_to_move = new_game_state.get_side_to_move()
        for i in range(100):
            self._clear_sq(i)
            self._spawn_piece_on_sq(i, board[i])

    def get_board(self):
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
