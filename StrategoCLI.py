"""
    This file is a Stratego game that can be played in console
"""

from src.Core.stratego import *
import random

from src.Core.stratego_gamestate import PieceType, _lake_set, _piece_type_setup_count, Side, verify_setup_dict, \
    game_state_from_setups


def generate_random_setup(side: Side) -> dict[int, PieceType]:
    setup = {}
    piece_counts = _piece_type_setup_count.copy()
    available_squares = list(range(60, 100)) if side == Side.blue else list(range(40))
    random.shuffle(available_squares)

    for piece_type, count in piece_counts.items():
        for _ in range(count):
            square = available_squares.pop()
            setup[square] = piece_type

    return setup


def print_board(game_state_view):
    skin = lambda x: x if x != "10" else "X"
    print("  ", end="")
    for i in range(10):
        print(f"{i} ", end="")
    print()
    for i in range(10):
        print(f"{i} ", end="")
        for j in range(10):
            token = game_state_view[i * 10 + j]
            if token:
                if token.type == "?":
                    print("\033[0;37;47m? \033[m", end="")  # White on black for unknown pieces
                else:
                    color_code = "\033[0;31m" if token.side == Side.red else "\033[0;34m"
                    if (i * 10 + j) in _lake_set:
                        print("\033[0;46m" + ". \033[m", end="")  # Cyan for lake squares
                    else:
                        print(f"{color_code}{skin(token.type)} \033[m", end="")  # Red for red pieces, blue for blue pieces
            else:
                if (i * 10 + j) in _lake_set:
                    print("\033[0;46m" + ". \033[m", end="")  # Cyan for lake squares
                else:
                    print(". ", end="")
        print()


def main():

    # Initialize game state
    game = GameInstance()

    # Create setups for red and blue sides
    red_setup = generate_random_setup(Side.red)

    blue_setup = generate_random_setup(Side.blue)

    # Verify setups
    if not verify_setup_dict(red_setup, Side.red) or not verify_setup_dict(blue_setup, Side.blue):
        print("Invalid setups!")
        return

    # Generate game state from setups
    game.set_game_state(game_state_from_setups(red_setup, blue_setup))

    print("Welcome to Stratego!")
    print("Commands:")
    print("   - move <from> <to>: Make a move (e.g., 'move 00 10')")
    print("   - quit: Quit the game")
    player_side = None
    while player_side not in ["red", "blue"]:
        player_side = input("Choose your side [red/blue]:").lower()
    player_side = Side.red if player_side == "red" else Side.blue
    print_board(game.get_view(player_side))

    while True:
        if game.get_side() is not player_side:
            if game.is_game_finish():
                print("Game Over!")
                break
            move_list = game.move_gen(game.get_side())
            game.execute_move(random.choice(move_list))
            print_board(game.get_view(player_side))
            continue
        command = input("\nEnter your command: ").strip().lower()
        if command == "quit":
            print("Quitting the game...")
            break
        elif command.startswith("move"):
            try:
                _, from_sq, to_sq = command.split()
                from_sq = int(from_sq)
                to_sq = int(to_sq)
                if not (0 <= from_sq < 100 and 0 <= to_sq < 100):
                    print("Invalid square(s)!")
                    continue
                if not game.is_move_legal((from_sq, to_sq)):
                    print("Invalid move!")
                    continue
                game.execute_move((from_sq, to_sq))
                print_board(game.get_view(player_side))
                if game.is_game_finish():
                    print("Game Over!")
                    break
            except ValueError:
                print("Invalid command format!")
        else:
            print("Invalid command!")


if __name__ == "__main__":
    main()
