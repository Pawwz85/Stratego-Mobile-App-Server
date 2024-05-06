"""
    For purposes of server Resource Manager, we need a data structure that
    1. is iterable
    2. has fast insert operation
    3. has fast remove operation

    Unfortunately python build in list has O(n) insert/removal time complexity.
    Fortunately we can use linked list for that purpose, making use from its
    operations time complexity of O(1) .
"""


class LinkedList:
    class LinkedListNode:
        def __init__(self, value):
            self.value = value
            self.prev: None | LinkedList.LinkedListNode = None
            self.next: None | LinkedList.LinkedListNode = None
            self.list = None

        def detach(self):
            if self.prev is not None:
                self.prev.next = self.next

            if self.next is not None:
                self.next.prev = self.prev

            if self.list is not None and self is self.list._head:
                self.list._head = self.next

            if self.list is not None:
                self.list._size -= 1
                self.list = None

    class _ListIterator:
        def __init__(self, node):
            self.node = node

        def __iter__(self):
            return self

        def __next__(self):
            if self.node is None:
                raise StopIteration
            result = self.node.value
            self.node = self.node.next
            return result

    def __init__(self):
        self._size = 0
        self._head = None

    def __iter__(self):
        return LinkedList._ListIterator(self._head)

    def __len__(self):
        return self._size

    def add(self, value) -> LinkedListNode:
        node = LinkedList.LinkedListNode(value)
        node.list = self
        if self._head is None:
            self._head = node
        else:
            self._head.prev = node
            node.next = self._head
            self._head = node
        self._size += 1
        return node

    def get_head(self) -> LinkedListNode:
        return self._head
