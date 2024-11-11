from src.Core.cstratego import CStrategoGameState, CStrategoMoveGenLibrary
from src.Core.stratego import GameInstance, PurePythonGameInstance


class DynamicLibraryNotFound(BaseException):
    pass


class GameInstanceFactory:
    def __init__(self):
        self.cstrategodll = CStrategoMoveGenLibrary.get_instance().cstrategodll

    @staticmethod
    def create_pure_python_game_instance() -> GameInstance:
        return PurePythonGameInstance()

    def create_c_game_instance(self) -> GameInstance:
        if self.cstrategodll is None:
            raise DynamicLibraryNotFound
        return CStrategoGameState(self.cstrategodll)

    def create_default(self) -> GameInstance:
        try:
            result = self.create_c_game_instance()
        except DynamicLibraryNotFound:
            result = self.create_pure_python_game_instance()
        return result
