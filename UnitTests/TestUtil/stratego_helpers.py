import json

import src.Core.stratego as stratego
import random

import src.Core.stratego_gamestate


def generate_random_setup(side: src.Core.stratego_gamestate.Side) -> dict[int, src.Core.stratego_gamestate.PieceType]:
    setup = {}
    piece_counts = src.Core.stratego_gamestate._piece_type_setup_count.copy()
    available_squares = list(range(60, 100)) if side == src.Core.stratego_gamestate.Side.red else list(range(40))
    random.shuffle(available_squares)

    for piece_type, count in piece_counts.items():
        for _ in range(count):
            square = available_squares.pop()
            setup[square] = piece_type
    assert src.Core.stratego_gamestate.verify_setup_dict(setup, side)
    return setup


def setup_to_protocol_form(setup: dict[int, src.Core.stratego_gamestate.PieceType]):
    result = []
    for sq, piece_type in setup.items():
        result.append({
            'sq': sq,
            'piece': src.Core.stratego_gamestate._piece_type_to_str[piece_type]
        })

    return result


def rand_move(game_state: stratego.GameInstance, side: src.Core.stratego_gamestate.Side) -> tuple[int, int]:
    try:
        moves = game_state.move_gen(side)
        return random.choice(moves)
    except Exception as e:
        print(json.dumps(game_state.get_board()))
        raise e


class FastWinPosition:
    def __init__(self, moving_side: src.Core.stratego_gamestate.Side):
        self.setups: dict = dict()
        self.moving_side = moving_side
        self.game_state = stratego.PurePythonGameInstance()
        self.winning_move = (0, 0)
        self.__fun_squares = {src.Core.stratego_gamestate.Side.red: 69, src.Core.stratego_gamestate.Side.blue: 39}
        self.create_fast_win_pos()

    def create_fast_win_pos(self):
        red_setup = generate_random_setup(src.Core.stratego_gamestate.Side.red)
        blue_setup = generate_random_setup(src.Core.stratego_gamestate.Side.blue)
        self.setups = {src.Core.stratego_gamestate.Side.red: red_setup, src.Core.stratego_gamestate.Side.blue: blue_setup}

        setup = self.setups[self.moving_side]
        for sq, type_ in setup.items():
            if type_ is src.Core.stratego_gamestate.PieceType.scout:
                setup[sq] = setup[self.__fun_squares[self.moving_side]]
                setup[self.__fun_squares[self.moving_side]] = src.Core.stratego_gamestate.PieceType.scout

        setup = self.setups[self.moving_side.flip()]
        for sq, type_ in setup.items():
            if type_ is src.Core.stratego_gamestate.PieceType.flag:
                setup[sq] = setup[self.__fun_squares[self.moving_side.flip()]]
                setup[self.__fun_squares[self.moving_side.flip()]] = src.Core.stratego_gamestate.PieceType.flag

        for side in self.setups:
            assert src.Core.stratego_gamestate.verify_setup_dict(self.setups[side], side)

        self.game_state = src.Core.stratego_gamestate.game_state_from_setups(red_setup, blue_setup)
        self.winning_move = (self.__fun_squares[self.moving_side], self.__fun_squares[self.moving_side.flip()])
