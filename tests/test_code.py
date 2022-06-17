import pytest
from tree.node import Node, SymlinkNode
from tree.exceptions import ReadOnlyError, FormulaError


def test_read_only():
    a = Node('a', read_only=True)
    Node('b', parent=a)
    with pytest.raises(ReadOnlyError):
        a.children = []


def test_formula():
    a = Node('a', formula='')
    with pytest.raises(FormulaError):
        a.calculate()



if __name__ == '__main__':
    pytest.main()
