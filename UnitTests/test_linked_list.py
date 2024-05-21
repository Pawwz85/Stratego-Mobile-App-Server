import unittest
import random

from src.DataStructures.linked_list import LinkedList


class TestLinkedList(unittest.TestCase):

    def test_addition(self):
        list = LinkedList()
        nr = random.random()
        list.add(nr)
        self.assertEqual(list.get_head().value, nr)

    def test_iteration_after_detach_from_middle(self):
        n = 20 # n >= 3!
        test_set = set()
        list = LinkedList()
        for i in range(n):
            list.add(i)

        list.get_head().next.next.detach()

        for i in list:
            test_set.add(i)

        self.assertEqual(len(test_set), n - 1)

    def test_clear(self):
        data = [i for i in range(100000)]
        random.shuffle(data)
        list = LinkedList()
        debug_count = 0
        try:
            for nr in data:
                list.add(nr)
                debug_count += 1

            for nr in data:
                list.get_head().detach()
                debug_count -= 1

        except:
            # print(data)
            print(debug_count)

        self.assertIs(list.get_head(), None)

    def test_insertion_after_clear(self):
        data = [i for i in range(100000)]
        random.shuffle(data)
        list = LinkedList()
        debug_count = 0
        try:
            for nr in data:
                list.add(nr)
                debug_count += 1

            for nr in data:
                list.get_head().detach()
                debug_count -= 1

            for nr in data:
                list.add(nr)
                debug_count += 1
        except:
            # print(data)
            print(debug_count)

        self.assertEqual(debug_count, len(list))
