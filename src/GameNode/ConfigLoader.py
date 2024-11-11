from __future__ import annotations

import json
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

_Default_Config = "Config/game_node_config.properties"


class _StrategyNotInFactoryDomainException(Exception):
    pass


class _ConfigLoader(ABC):

    @abstractmethod
    def reset_builder(self) -> _ConfigLoader:
        pass

    @abstractmethod
    def load_config(self) -> dict | None:
        pass


class ConfigLoaderStrategy(Enum):
    LoadFromDefaultJsonFile = 0
    LoadFromCustomJsonFile = 1
    LoadFromJsonString = 2


class IConfigLoaderFactory(ABC):
    def __init__(self):
        self.allowed_strategies = set()

    def build_config(self, strategy: ConfigLoaderStrategy, *args, **kwargs):
        if strategy not in self.allowed_strategies:
            raise _StrategyNotInFactoryDomainException()
        return self._build_loader(strategy, *args, **kwargs).load_config()

    @abstractmethod
    def _build_loader(self, strategy: ConfigLoaderStrategy, *args, **kwargs) -> _ConfigLoader:
        pass


class JsonFileConfigLoader(_ConfigLoader):

    def __init__(self):
        self.path: Path | None = None

    def reset_builder(self) -> _ConfigLoader:
        self.path = None
        return self

    def load_config(self) -> dict | None:
        with open(self.path) as file:
            result = json.load(file)
        return result

    def set_path(self, p: Path):
        self.path = p
        return self


class JsonStringConfigLoader(_ConfigLoader):

    def __init__(self):
        self.json_string: str | None = None

    def load_config(self) -> dict | None:
        return json.loads(self.json_string)

    def reset_builder(self) -> _ConfigLoader:
        self.json_string = None
        return self

    def set_string(self, string: str):
        self.json_string = string
        return self


class JsonConfigLoaderFactory(IConfigLoaderFactory):
    def __init__(self):
        super().__init__()
        self.allowed_strategies = {ConfigLoaderStrategy.LoadFromJsonString,
                                   ConfigLoaderStrategy.LoadFromCustomJsonFile,
                                   ConfigLoaderStrategy.LoadFromDefaultJsonFile}

    def _build_loader(self, strategy: ConfigLoaderStrategy, *args, **kwargs) -> _ConfigLoader:

        if strategy is ConfigLoaderStrategy.LoadFromDefaultJsonFile:
            return JsonFileConfigLoader().set_path(Path(_Default_Config))
        elif strategy is ConfigLoaderStrategy.LoadFromCustomJsonFile:
            return JsonFileConfigLoader().set_path(kwargs["file"])
        else:
            return JsonStringConfigLoader().set_string(kwargs["json_string"])

