from __future__ import annotations
import unittest
from src.Core.singleton import singleton, SingletonException


@singleton
class ExampleSingleton:
    def __init__(self):
        self.some_variable = 7

    @staticmethod
    def get_instance() -> ExampleSingleton:
        pass


@singleton
class ExampleSingleton2:
    def __init__(self, some_var):
        self.some_var = some_var

    @staticmethod
    def get_instance(some_var) -> ExampleSingleton2:
        pass


class SingletonSuite(unittest.TestCase):
    def test_exception(self):
        self.assertRaises(SingletonException, ExampleSingleton.__init__)

    def test_get_instance(self):
        instance1 = ExampleSingleton.get_instance()
        instance2 = ExampleSingleton.get_instance()
        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.some_variable, 7)

    def test_singleton2_init(self):
        instance1 = ExampleSingleton2.get_instance(2)
        instance2 = ExampleSingleton2.get_instance(3)
        self.assertEqual(instance1.some_var, 2)

