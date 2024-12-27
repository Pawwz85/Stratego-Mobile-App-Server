import json
import os
import unittest
from pathlib import Path
from unittest.mock import Mock

import src.ConfigLoader as ConfigLoader
from src.ConfigLoader import ConfigLoaderStrategy


class IConfigLoaderFactoryTestCase(unittest.TestCase):
    class MockedConfigFactory(ConfigLoader.IConfigLoaderFactory):
        def _build_loader(self, strategy: ConfigLoaderStrategy, *args, **kwargs):
            pass

        def __init__(self):
            super().__init__()
            self.allowed_strategies = {ConfigLoader.ConfigLoaderStrategy.LoadFromCustomJsonFile}

    def setUp(self):
        self.factory = self.MockedConfigFactory()
        self.factory._build_loader = Mock()

    def tearDown(self):
        del self.factory

    def test_factory_raises_exception_for_strategy_outside_domain(self):
        self.assertRaises(ConfigLoader._StrategyNotInFactoryDomainException,
                          self.factory.build_config,
                          ConfigLoader.JsonStringConfigLoader, json_string="{some_var: 7}")


class TestJsonStringConfigLoader(unittest.TestCase):
    def setUp(self):
        self.json_str = "{\"some_var\": 7}"
        self.factory = ConfigLoader.JsonConfigLoaderFactory()

    def tearDown(self):
        del self.json_str, self.factory

    def test_valid_load(self):
        config = self.factory.build_config(ConfigLoader.ConfigLoaderStrategy.LoadFromJsonString,
                                           json_string=self.json_str)
        self.assertEqual(config["some_var"], 7)

    def test_invalid_string(self):
        self.assertRaises(json.JSONDecodeError, self.factory.build_config,
                          ConfigLoader.ConfigLoaderStrategy.LoadFromJsonString,
                          json_string="7_-")


class TestJsonFileConfigLoader(unittest.TestCase):
    def setUp(self):
        self.json_str = "{\"some_var\": 7}"
        self.factory = ConfigLoader.JsonConfigLoaderFactory()
        with open("TestJsonFileConfigLoader.json", "a") as file:
            file.write(self.json_str)
        with open("TestJsonFileConfigLoader2.json", "a") as file:
            file.write("7-_")

    def tearDown(self):
        del self.json_str, self.factory
        os.remove("TestJsonFileConfigLoader.json")
        os.remove("TestJsonFileConfigLoader2.json")

    def test_valid_load(self):
        config = self.factory.build_config(ConfigLoader.ConfigLoaderStrategy.LoadFromCustomJsonFile,
                                           file=Path("TestJsonFileConfigLoader.json"))
        self.assertEqual(config["some_var"], 7)

    def test_no_file(self):
        self.assertRaises(FileNotFoundError, self.factory.build_config,
                          ConfigLoader.ConfigLoaderStrategy.LoadFromCustomJsonFile,
                          file=Path("TestNotExistingJsonFileConfigLoader.json"))

    def test_invalid_file(self):
        self.assertRaises(json.JSONDecodeError, self.factory.build_config,
                          ConfigLoader.ConfigLoaderStrategy.LoadFromCustomJsonFile,
                          file=Path("TestJsonFileConfigLoader2.json"))


if __name__ == '__main__':
    unittest.main()
