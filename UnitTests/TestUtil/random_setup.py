import src.Core.stratego as stratego
import random


def generate_random_setup(side: stratego.Side) -> dict[int, stratego.PieceType]:
    setup = {}
    piece_counts = stratego._piece_type_setup_count.copy()
    available_squares = list(range(60, 100)) if side == stratego.Side.red else list(range(40))
    random.shuffle(available_squares)

    for piece_type, count in piece_counts.items():
        for _ in range(count):
            square = available_squares.pop()
            setup[square] = piece_type

    return setup