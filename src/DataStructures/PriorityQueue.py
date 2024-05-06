"""
    Priority Queue implementation based on red black trees
"""
from src.DataStructures.BlackRedTree import BlackRedTree


class PriorityQueue:
    class __PrioritizedKey:
        def __init__(self, key, priority):
            self.key = key
            self.priority = priority

        def __eq__(self, other):
            return self.priority == other.priority and self.key == other.key

        def __gt__(self, other):
            return self.priority > other.priority

        def __lt__(self, other):
            return self.priority < other.priority

    def __init__(self):
        self.__tree = BlackRedTree()

    def __len__(self):
        return len(self.__tree)

    def add(self, priority, key, value):
        priority_key = PriorityQueue.__PrioritizedKey(key, priority)
        self.__tree.add(priority_key, value)
        return priority_key

    def remove(self, key):
        self.__tree.delete(key)

    def get_top(self):
        result = self.__tree.greatest()
        return result
