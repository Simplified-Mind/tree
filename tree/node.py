"""Reactive Node
Examples:
    >>> import pandas as pd
    >>> from tree import Node, SymlinkNode
    >>> a = Node('a', formula='b + c')
    >>> b = Node('b', parent=a)
    >>> c = Node('c', parent=a, formula='s + t')
    >>> s = Node('s', parent=c)
    >>> t = Node('t', parent=c)
    >>> a.pprint()
        a        b + c
    ├── b
    └── c        s + t
        ├── s
        └── t
    >>> a.to_json()
    {"name": "a", "is_dirty": false, "children": [{"name": "b", "is_dirty": false}, {"name": "c", "is_dirty": false, "children": [{"name": "s", "is_dirty": false}, {"name": "t", "is_dirty": false}]}]}
    >>> x = Node('x', formula='y + c')
    >>> y = Node('y', parent=x)
    >>> z = SymlinkNode(c, parent=x)
    >>> x.pprint()
        x        y + c
    ├── y
    └── c        s + t
    >>> x.to_json()
    {"name": "x", "is_dirty": false, "children": [{"name": "y", "is_dirty": false}, {"name": "c", "is_dirty": false, "formula": "s + t"}]}
    >>> v = pd.Series([1], dtype='float64')
    >>> s.series = v
    >>> t.series = v
    >>> pd.testing.assert_series_equal(c.series, v + 1)
    >>> b.series = pd.Series([1], dtype='float64')
    >>> pd.testing.assert_series_equal(a.series, v + 2)
    >>> c.series = pd.Series([1], dtype='float64')
    >>> pd.testing.assert_series_equal(a.series, pd.Series([2], dtype='float64'))
    >>> a.pprint()
        a 🚩      b + c
    ├── b 🚩
    └── c 🚩      s + t
        ├── s 🚩
        └── t 🚩
    >>> x.pprint()
        x 🚩      y + c
    ├── y
    └── c 🚩      s + t

The module contains the following classes:

- `Node`
- `SymlinkNode`

"""

import os
from json import dumps
from warnings import warn
from typing import Literal, List, Any, Callable, Type
from ast import parse, Assign, unparse

import pandas as pd
from loguru import logger
from tree.utils import FormulaTransformer
from tree.exceptions import ReadOnlyError, FormulaError, MissingFormula

from anytree.node import NodeMixin, SymlinkNodeMixin
from anytree.node.util import _repr
from anytree.exporter import DictExporter
from anytree.util import leftsibling, rightsibling
from anytree import RenderTree, AbstractStyle, ContStyle


class Node(NodeMixin):
    """Reactive Node"""
    def __init__(
        self,
        name: str,
        desc: str = '',
        series: pd.Series = None,
        assert_series_equal: bool = True,
        formula: str = '',
        funcs_path: str = None,
        trigger_type: Literal['any', 'all'] = 'any',
        is_trigger_event: bool = True,
        is_deferred: bool = False,
        read_only: bool = False,
        parent: Type[NodeMixin] = None,
        children: Type[NodeMixin] = None,
    ):
        self.name = name
        self.desc = desc
        self._series = series if series else pd.Series(dtype='float64')

        # Only reassign the series if the new value is different from the existing one
        self.assert_series_equal = assert_series_equal

        # Prevent the user to change the children if read_only is True
        self.read_only = read_only

        # Flag if the series has been updated
        self.is_dirty = False

        # Flag if the series is being updated by the remote
        self.is_locked = False
        self._formula = formula
        self._funcs_path = funcs_path if funcs_path else os.path.join(os.path.dirname(__file__), 'functions.py')
        self._registered_functions = []
        self._statement = None
        self._statement_ast = None

        # Define when the node can be updated
        # 1. 'all' - update the node when children are changed
        # 2. 'any' - update the node when a child is changed
        self.trigger_type = trigger_type

        # Flag if node change will trigger the parent to be re-calculated
        self.is_trigger_event = is_trigger_event

        # Flag if the node should be updated immediately if all the conditions are passed
        self.is_deferred = is_deferred

        # Keep track of the symbolic nodes
        self.book = {}

        self.parent = parent
        if children:
            self.children = children

    def _pre_attach(self, parent: Type[NodeMixin]) -> Any:
        if self.root.read_only:
            raise ReadOnlyError()

    def _pre_detach(self, parent: Type[NodeMixin]) -> Any:
        if self.root.read_only:
            raise ReadOnlyError()

    @property
    def left_sibling(self):
        return leftsibling(self)

    @property
    def right_sibling(self):
        return rightsibling(self)

    @property
    def funcs_path(self):
        return self._funcs_path

    @funcs_path.setter
    def funcs_path(self, value: str):
        if not isinstance(value, str):
            raise TypeError('Expected a string!')
        self._funcs_path = value
        self._registered_functions = self.get_registered_functions()

    def get_registered_functions(self) -> List[str]:
        with open(self.funcs_path) as file:
            tree = parse(file.read())
            for node in tree.body:
                if isinstance(node, Assign):
                    return [e.value for e in node.value.elts]

    @property
    def registered_functions(self) -> List[str]:
        return self._registered_functions

    @property
    def can_recalculate_parent(self) -> bool:
        flag = False
        if not self.is_root:
            if not self.parent.is_deferred and not self.parent.is_locked:
                if self.parent.trigger_type == 'any':
                    if all((self.is_dirty, self.is_trigger_event, not self.is_locked)):
                        flag = True
                else:
                    flag = True

                    for s in self.siblings:
                        if not s.is_trigger_event:
                            pass
                        else:
                            if not s.is_dirty or s.is_locked:
                                flag = False
                                break
        return flag

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, value: str) -> Any:
        if not isinstance(value, str):
            raise TypeError('Expected a string!')

        v = self.registered_functions + ['self']
        e = ['from tree.functions import *']
        for i, c in enumerate(self.children):
            v.append(c.name)
            e.append(f'{c.name} = self.children[{i}].series')
        e.append(f'self.series = {value}')
        self._statement = '\n'.join(e)
        try:
            self._statement_ast = parse(self._statement)
        except SyntaxError:
            raise SyntaxError(f'Invalid formula: "{value}"')

        try:
            FormulaTransformer(v).visit(self._statement_ast)
        except FormulaError:
            self._statement, self._statement_ast = None, None
            raise
        else:
            self._formula = value

    @property
    def series(self) -> pd.Series:
        return self._series

    @series.setter
    def series(self, value: pd.Series) -> Any:
        if not isinstance(value, pd.Series):
            raise TypeError('Expected a pd.Series')

        flag = True
        if self.assert_series_equal:
            try:
                pd.testing.assert_series_equal(self._series, value)
            except AssertionError:
                pass
            else:
                flag = False

        if flag:
            self._series = value
            self.is_dirty = True

            if self.can_recalculate_parent:
                logger.debug(f"'{self.parent.name}' is triggered by the node '{self.name}'")
                self.parent.calculate()

            for key, value in self.book.items():
                if value.can_recalculate_parent:
                    logger.debug(f"'{value.parent.name}' is triggered by the symbolic node '{value.name}'")
                    value.parent.calculate()

    @property
    def dataframe(self) -> pd.DataFrame:
        if self.is_leaf:
            return self.series.to_frame()
        else:
            data, name = [], []
            [(data.append(child.series), name.append(child.name)) for child in self.children]
            return pd.concat(data, axis=1, keys=name)

    def calculate(self) -> Any:
        if not self.children:
            raise FormulaError('No children found!')

        if self.formula:
            if self._statement_ast is None:
                self.formula = self.formula
            exec(unparse(self._statement_ast))
        else:
            warn('No formula to evaluate!', MissingFormula)

    def to_dict(
        self,
        dict_cls=dict,
        attr_iter: Callable = None,
        child_iter: Callable = list,
        max_level: int = None,
    ) -> dict:
        def default_attr_iter(attrs: List[tuple]) -> List[tuple]:
            lst = []
            for (k, v) in attrs:
                if k in ['name', 'is_dirty', 'formula']:
                    lst.append((k, v))
                elif k == 'target':
                    lst += [('name', v.name), ('is_dirty', v.is_dirty), ('formula', v.formula)]
            return lst

        exporter = DictExporter(
            dictcls=dict_cls,
            attriter=attr_iter if attr_iter else default_attr_iter,
            childiter=child_iter,
            maxlevel=max_level
        )
        return exporter.export(self)

    def to_json(
        self,
        dict_cls=dict,
        attr_iter: Callable = None,
        child_iter: Callable = list,
        max_level: int = None,
    ) -> str:
        result = self.to_dict(dict_cls, attr_iter, child_iter, max_level)
        return dumps(result)

    def pprint(
        self,
        style: Type[AbstractStyle] = ContStyle(),
        child_iter: Callable = list,
        max_level: int = None,
        length: int = 12,
    ) -> None:
        for pre, _, node in RenderTree(self, style=style, childiter=child_iter, maxlevel=max_level):
            tree = f'{pre}{node.name}{" 🚩" if node.is_dirty else ""}'
            print(tree.ljust(length), node.formula)

    def __repr__(self) -> str:
        args = ['%r' % self.separator.join([''] + [str(node.name) for node in self.path])]
        return _repr(self, args=args, nameblacklist=('name', ))


class SymlinkNode(SymlinkNodeMixin):
    """Symbolic Node"""
    def __init__(self, target, parent=None, children=None, **kwargs):
        self.target = target
        self.target.__dict__.update(kwargs)
        self.parent = parent
        if children:
            self.children = children

        self._abs_path = None

    def abs_path(self):
        if self._abs_path is None:
            self._abs_path = self.separator.join([x.name for x in self.path])
        return self._abs_path

    def _post_attach(self, parent) -> Any:
        self.target.book[self.abs_path] = self

    def _post_detach(self, parent) -> Any:
        del self.target.book[self.abs_path]

    def __repr__(self):
        return _repr(self, [repr(self.target)], nameblacklist=('target', ))


if __name__ == '__main__':
    data = """
    a: root
    children:
    - a: sub0
      children:
      - a: sub0A
        b: foo
      - a: sub0B
    - a: sub1
    
    c: root
    children:
    - c: sub0
      children:
      - c: sub0A
        b: foo
      - c: sub0B
    - c: sub1
    """
