"""
    For purposes of implementing a delayed tasks, we need a priority queue data structure with
    ability to remove any item from the structure.

    Characteristics:
    - Insert: Log O(log N)
    - Delete: Log O(log N)
    - Look up: Log O(log N)

"""
from __future__ import annotations

from enum import Enum
from typing import Callable


class BlackRedTree:
    class Color(Enum):
        BLACK = 0,
        RED = 1

    class RotationDirection(Enum):
        LEFT = 0,
        RIGHT = 1

        def mirror(self):
            if self is BlackRedTree.RotationDirection.RIGHT:
                return BlackRedTree.RotationDirection.LEFT
            else:
                return BlackRedTree.RotationDirection.RIGHT

    class Node:
        def __init__(self, key, value):
            self.data = value
            self.key = key
            self.parent: BlackRedTree.Node | None = None
            self.left_son: BlackRedTree.Node | None = None
            self.right_son: BlackRedTree.Node | None = None
            self.color: BlackRedTree.Color = BlackRedTree.Color.RED

    def __init__(self):
        self._root: BlackRedTree.Node | None = None
        self._size = 0

    def _rotation(self, node: BlackRedTree.Node, dir: BlackRedTree.RotationDirection) -> BlackRedTree.Node:

        update_root: bool = node is self._root
        ascending_node = node.left_son if dir is BlackRedTree.RotationDirection.RIGHT else node.right_son
        assert ascending_node is not None

        grandparent = node.parent
        # swap parents
        node.parent = ascending_node
        ascending_node.parent = grandparent

        if dir is BlackRedTree.RotationDirection.RIGHT:
            middle_node = ascending_node.right_son
            ascending_node.right_son = node
            node.left_son = middle_node
        else:
            middle_node = ascending_node.left_son
            ascending_node.left_son = node
            node.right_son = middle_node

        if middle_node is not None:
            middle_node.parent = node

        if grandparent is not None:
            if node is grandparent.left_son:
                grandparent.left_son = ascending_node
            else:
                grandparent.right_son = ascending_node

        if update_root:
            self._root = ascending_node

        return ascending_node

    def _bst_search(self, key):
        node = self._root
        while node is not None:
            if node.key == key:
                return node
            node = node.left_son if (node.key > key) else node.right_son
        return None

    def search(self, key):
        x = self._bst_search(key)
        return x.data if x is not None else None

    def _bst_style_insert(self, key, value):
        node = BlackRedTree.Node(key, value)
        if self._root is None:
            self._root = node
            node.color = BlackRedTree.Color.BLACK
            return self._root
        i = self._root
        j = None
        while i is not None:
            j = i
            i = i.left_son if (i.key > key) else i.right_son
        node.parent = j
        if j.key > key:
            j.left_son = node
        else:
            j.right_son = node

        return node

    def __del_case3(self, s: Node, c: Node,  p: Node, _dir: RotationDirection):
        self._rotation(p, _dir)
        p.color = BlackRedTree.Color.RED
        s.color = BlackRedTree.Color.BLACK
        s = c
        d = s.left_son if _dir is BlackRedTree.RotationDirection.RIGHT else s.right_son
        if d is not None and d.color is BlackRedTree.Color.RED:
            self.__del_case6(s, d, p, _dir)
            return
        c = s.left_son if _dir is BlackRedTree.RotationDirection.LEFT else s.right_son
        if c is not None and c.color is BlackRedTree.Color.RED:
            self.__del_case5(s, c, p, _dir)
            return

        BlackRedTree.__del_case4(s, p)

    @staticmethod
    def __del_case4(s: Node, p: Node):
        s.color = BlackRedTree.Color.RED
        p.color = BlackRedTree.Color.BLACK

    def __del_case5(self, s: Node, c: Node, p: Node, _dir: RotationDirection):

        d = s.left_son if _dir is BlackRedTree.RotationDirection.RIGHT else s.right_son
        self._rotation(s, _dir.mirror())
        s.color = BlackRedTree.Color.RED
        c.color = BlackRedTree.Color.BLACK
        d = s
        s = c
        self.__del_case6(s, d, p, _dir)

    def __del_case6(self, s: Node, d: Node, p: Node, _dir: RotationDirection):
        self._rotation(p, _dir)
        s.color = p.color
        p.color = d.color = BlackRedTree.Color.BLACK

    def _restore_property_after_insert(self, insertion_node: Node):
        z = insertion_node
        z.color = BlackRedTree.Color.RED

        if z is self._root:
            z.color = BlackRedTree.Color.BLACK
            return

        while z is not None:
            p = z.parent

            if p is None:
                return

            if p.color is BlackRedTree.Color.BLACK:
                return

            if p.parent is None:
                # parent is red and root
                p.color = BlackRedTree.Color.BLACK
                return

            g = p.parent
            if p is g.left_son:
                _dir = BlackRedTree.RotationDirection.LEFT
                u = g.right_son
            else:
                _dir = BlackRedTree.RotationDirection.RIGHT
                u = g.left_son

            if u is None or u.color is BlackRedTree.Color.BLACK:

                if z is (p.left_son if _dir is BlackRedTree.RotationDirection.RIGHT else p.right_son):
                    self._rotation(p, _dir)
                    z = p
                    p = z.parent
                self._rotation(g, _dir.mirror())
                p.color = BlackRedTree.Color.BLACK
                g.color = BlackRedTree.Color.RED
                return

            p.color = BlackRedTree.Color.BLACK
            u.color = BlackRedTree.Color.BLACK
            g.color = BlackRedTree.Color.RED
            z = g

    def _remove_node(self, node: BlackRedTree.Node):
        nr_of_children = 0
        if node.left_son is not None:
            nr_of_children += 1
        if node.right_son is not None:
            nr_of_children += 1

        if nr_of_children == 2:
            successor = BlackRedTree.__find_successor(node)
            node.data = successor.data
            node.key = successor.key
            self._remove_node(successor)
            return

        if nr_of_children == 1:
            child = node.left_son if node.right_son is None else node.right_son
            node.key = child.key
            node.data = child.data
            node.left_son = child.left_son
            if node.left_son is not None:
                node.left_son.parent = node
            node.right_son = child.right_son
            if node.right_son is not None:
                node.right_son.parent = node
            node.color = BlackRedTree.Color.BLACK
            return

        if node is self._root:
            self._root = None
            return

        if node.color is BlackRedTree.Color.RED:
            if node.parent.left_son is node:
                node.parent.left_son = None
            else:
                node.parent.right_son = None
            node.parent = None
            return

        p = node.parent
        if node is p.left_son:
            p.left_son = None
            s = p.right_son
            d = s.right_son
            c = s.left_son
            _dir = BlackRedTree.RotationDirection.LEFT
        else:
            p.right_son = None
            s = p.left_son
            c = s.right_son
            d = s.left_son
            _dir = BlackRedTree.RotationDirection.RIGHT
        node.parent = None
        node = None

        while node is None or node.parent is not None:
            if node is not None:
                p: BlackRedTree.Node = node.parent
                if node is p.left_son:
                    s: BlackRedTree.Node = p.right_son
                    d = s.right_son
                    c = s.left_son
                    _dir = BlackRedTree.RotationDirection.LEFT

                elif node is p.right_son:
                    s: BlackRedTree.Node = p.left_son
                    d = s.left_son
                    c = s.right_son
                    _dir = BlackRedTree.RotationDirection.RIGHT

            if s.color is BlackRedTree.Color.RED:
                self.__del_case3(s, c, p, _dir)
                return

            if d is not None and d.color is BlackRedTree.Color.RED:
                self.__del_case6(s, d, p, _dir)
                return

            if c is not None and c.color is BlackRedTree.Color.RED:
                self.__del_case5(s, c, p, _dir)
                return

            if p.color is BlackRedTree.Color.RED:
                BlackRedTree.__del_case4(s, p)
                return

            s.color = BlackRedTree.Color.RED
            node = p

        # print("Iter ended")

    def add(self, key, value):
        x = self._bst_style_insert(key, value)
        self._size += 1
        if x is self._root:
            x.color = BlackRedTree.Color.BLACK
        elif x.parent is not None and x.parent.color is BlackRedTree.Color.RED:
            self._restore_property_after_insert(x)

    def delete(self, key):
        x = self._bst_search(key)
        if x is not None:
            self._size -= 1
            self._remove_node(x)

    @staticmethod
    def __check_if_properties_hold(node: Node | None):
        red_have_red_child = False
        if node is None:
            return False, False, False, 0

        black_count = 0
        if node.color is BlackRedTree.Color.RED:
            if node.right_son is not None and node.right_son.color is BlackRedTree.Color.RED:
                red_have_red_child = True
            if node.left_son is not None and node.left_son.color is BlackRedTree.Color.RED:
                red_have_red_child = True
        else:
            black_count += 1

        left_key = None if node.left_son is None else node.left_son.key
        right_key = None if node.right_son is None else node.right_son.key

        red_viol1, black_violation1, bst_viol1, c1 = BlackRedTree.__check_if_properties_hold(node.left_son)
        red_viol2, black_violation2, bst_viol2, c2 = BlackRedTree.__check_if_properties_hold(node.right_son)

        return (red_viol1 or red_viol2 or red_have_red_child,
                c1 != c2 or black_violation1 or black_violation2,
                (left_key is not None and left_key > node.key) or
                (right_key is not None and right_key < node.key) or
                bst_viol1 or bst_viol2,
                black_count + c1)

    def __len__(self):
        return self._size

    def verify(self):
        red_viol, black_viol, bst_viol, _ = BlackRedTree.__check_if_properties_hold(self._root)
        if red_viol:
            raise Exception("Red violation")
        if black_viol:
            raise Exception("Black violation")
        if bst_viol:
            raise Exception("BST violation")

    def greatest(self):
        i = self._root
        j = None
        while i is not None:
            j = i
            i = i.right_son
        return None if j is None else j.data

    @staticmethod
    def __find_successor(node: Node) -> None | Node:
        i = node.right_son
        j = None
        while i is not None:
            j = i
            i = i.left_son
        return j

    @staticmethod
    def __in_order(node: Node, fun: Callable[[Node], any]):
        if node.left_son is not None:
            BlackRedTree.__in_order(node.left_son, fun)
        fun(node)
        if node.right_son is not None:
            BlackRedTree.__in_order(node.right_son, fun)
