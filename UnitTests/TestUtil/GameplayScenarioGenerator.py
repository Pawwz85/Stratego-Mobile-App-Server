"""
    This file allows to dynamically create a gameplay interaction between users
    and save it into format that it is an acceptable by User Simulation Interpreter
"""
from __future__ import annotations
import json
import random

from src.Core.stratego import GameInstance
from src.Core.stratego_gamestate import _piece_type_setup_count, Side, _piece_type_to_str, game_state_from_setups
from typing import Callable


class GameplayScenarioGenerator:

    def __init__(self, ai: Callable[[GameInstance, Side], tuple[int, int]] = None):
        self.game_state = GameInstance()
        if ai is not None:
            self.ai = ai
        else:
            self.ai = GameplayScenarioGenerator._rand_move

    @staticmethod
    def _rand_move(game_state: GameInstance, side: Side) -> tuple[int, int]:
        try:
            moves = game_state.move_gen(side)
            return random.choice(moves)
        except Exception as e:
            print(json.dumps(game_state.get_board()))
            raise e

    @staticmethod
    def __random_setup(side: Side):
        setup = {}
        piece_counts = _piece_type_setup_count.copy()
        available_squares = list(range(60, 100)) if side == Side.red else list(range(40))
        random.shuffle(available_squares)

        for piece_type, count in piece_counts.items():
            for _ in range(count):
                square = available_squares.pop()
                setup[square] = piece_type

        return setup

    def assume_random_setup(self, red_player_name, blue_player_name, interval_ms: int = 100) -> str:
        """
        Sets a random starting position as the game state.
        :param red_player_name:
        :param blue_player_name:
        :param interval_ms: An amount of ms between users sending their setups
        :return: Returns user simulation interpreter script, that simulates this setup
        """
        result = "$TableApi\n"
        result += f"AUTOWAIT TRUE {interval_ms}\n"
        players = {Side.red: red_player_name, Side.blue: blue_player_name}
        setups = {}
        for side in players.keys():
            setup = GameplayScenarioGenerator.__random_setup(side)
            setups[side] = setup
            setup = {"setup": [{"sq": k, "piece": _piece_type_to_str[v]} for k, v in setup.items()]}
            result += f"{players[side]} submit_setup > {json.dumps(setup)} \n"
        result += "AUTOWAIT FALSE"

        setup = game_state_from_setups(setups[Side.red], setups[Side.blue])
        self.game_state.set_game_state(setup)
        return result

    def simulate_gameplay(self, red_player_name, blue_player_name, interval_ms: int = 5):
        result = "$TableApi\n"
        result += f"AUTOWAIT TRUE {interval_ms}\n"
        while not self.game_state.is_game_finish():
            nickname = red_player_name if self.game_state.get_side() is Side.red else blue_player_name
            move = self.ai(self.game_state, self.game_state.get_side())
            self.game_state.execute_move(move)
            result += f'{nickname} make_move > {json.dumps({"move": {"from": move[0], "to": move[1]}})}\n'
        result += "AUTOWAIT FALSE"
        return result

    def create_match(self):
        setup = game_state_from_setups(self.__random_setup(Side.red), self.__random_setup(Side.blue))
        gs = GameInstance()
        gs.set_game_state(setup)

        while not gs.is_game_finish():
            yield gs
            move = self.ai(gs, gs.get_side())
            gs.execute_move(move)
