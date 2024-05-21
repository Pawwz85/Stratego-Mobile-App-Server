import unittest
import random
import src.DataStructures.BlackRedTree as brtree


class BlackRedTreeTestCase(unittest.TestCase):

    def test_for_addition_crash(self):
        data = [i for i in range(100000)]
        random.shuffle(data)
        tree = brtree.BlackRedTree()

        try:
            for i, nr in enumerate(data):
                tree.add(nr, None)

            tree.verify()
        except:
            # print(data)
            self.assertEqual(True, False)

    def test_search_addition_only(self):
        existing_data = [i for i in range(100000)]
        unexisting_data = [i for i in range(100000, 200000)]
        random.shuffle(existing_data)
        random.shuffle(unexisting_data)
        tree = brtree.BlackRedTree()
        for i in existing_data:
            tree.add(i, i)

        random.shuffle(existing_data)
        for i in existing_data:
            self.assertEqual(tree.search(i), i)

        for i in unexisting_data:
            self.assertIs(tree.search(i), None)

    def test_search(self):
        existing_data = [i for i in range(50000)]
        unexisting_data = [i for i in range(50000, 100000)]
        data = existing_data + unexisting_data
        random.shuffle(data)
        random.shuffle(existing_data)
        random.shuffle(unexisting_data)
        tree = brtree.BlackRedTree()

        for nr in data:
            tree.add(nr, nr)

        for nr in unexisting_data:
            tree.delete(nr)

        for nr in existing_data:
            self.assertEqual(nr, tree.search(nr))

        for nr in unexisting_data:
            self.assertIs(tree.search(nr), None)

    def test_deletion_for_crash(self):
        data = [i for i in range(100000)]
        random.shuffle(data)
        tree = brtree.BlackRedTree()
        debug_count = 0
        try:
            for nr in data:
                tree.add(nr, nr)

            random.shuffle(data)

            for nr in data:
                tree.delete(nr)
                debug_count += 1
                # tree.verify()

            tree.verify()

        except:
            # print(data)
            print(debug_count)
            tree.verify()
            self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
