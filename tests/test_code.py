import pytest
import pandas as pd
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

    b = Node('b', parent=a)
    a.formula = 'b + 1'
    b.series = pd.Series([1], dtype='float64')
    pd.testing.assert_series_equal(a.series, pd.Series([2], dtype='float64'))

    with pytest.raises(FormulaError):
        a.formula = '2*c'


def test_is_deferred():
    a = Node('a', formula='b + 1', is_deferred=True)
    b = Node('b', parent=a)
    b.series = pd.Series([1], dtype='float64')
    pd.testing.assert_series_equal(a.series, pd.Series(dtype='float64'))


def test_is_locked():
    a = Node('a', formula='b + 1')

    b = Node('b', parent=a, assert_series_equal=False)

    a.is_locked = True
    b.series = pd.Series([1], dtype='float64')
    pd.testing.assert_series_equal(a.series, pd.Series(dtype='float64'))


def test_symlink_node():
    a = Node('a', formula='a + b')
    b = Node('b', parent=a)
    c = Node('c', parent=a, formula='s + t')
    s = Node('s', parent=c)
    t = Node('t', parent=c)

    x = Node('x', formula='x + y + w')
    y = Node('y', parent=x)
    z = SymlinkNode(c, parent=x)


if __name__ == '__main__':
    pytest.main()
