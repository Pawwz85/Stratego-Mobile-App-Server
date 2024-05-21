import unittest

import src.FrontendBackendBridge.IBackendCaller as BackendCaller
from src.FrontendBackendBridge.FrontendChannelListener import BackendResponseStrategy


class TestIBackendCaller (unittest.TestCase):

    def test_wrap_strategy_with_mapping(self):
        called = 0
        original_id = "original_id"
        new_id = "new_id"
        unwrapped_strategy = BackendResponseStrategy(original_id, lambda x: self.assertEqual(x["response_id"], original_id) )

        wrapped_strategy = BackendCaller.IBackendCaller.wrap_strategy_with_mapping(
            original_id, new_id, unwrapped_strategy
        )
        response = {"response_id": new_id}

        wrapped_strategy(response)
        self.assertNotEqual(0, unwrapped_strategy.get_times_applied())

    def test_wrap_strategy_with_mapping_original_None(self):
        called = 0
        original_id = None
        new_id = "new_id"
        unwrapped_strategy = BackendResponseStrategy(original_id, lambda x: self.assertEqual(x["response_id"], original_id) )

        wrapped_strategy = BackendCaller.IBackendCaller.wrap_strategy_with_mapping(
            original_id, new_id, unwrapped_strategy
        )
        response = {"response_id": new_id}

        wrapped_strategy(response)
        self.assertNotEqual(0, unwrapped_strategy.get_times_applied())

    def test_wrap_strategy_with_mapping_mismatch(self):
        called = 0
        original_id = "original_id"
        new_id = "new_id"
        unwrapped_strategy = BackendResponseStrategy(original_id, lambda x: self.assertEqual(0, 1) )

        wrapped_strategy = BackendCaller.IBackendCaller.wrap_strategy_with_mapping(
            original_id, new_id, unwrapped_strategy
        )
        response = {"response_id": "some_other_id"}

        wrapped_strategy(response)
        self.assertEqual(0, unwrapped_strategy.get_times_applied())