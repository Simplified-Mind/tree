"""Utilities

Examples:
    >>> from tree import FormulaTransformer
    >>> from ast import parse
    >>> expression = 'b + c'
    >>> FormulaTransformer(['a']).visit(parse(expression))
    Traceback (most recent call last):
     ...
    tree.exceptions.FormulaError: Please use registered keywords.

The module contains the following classes/functions:

- `FormulaTransformer`
"""


from typing import List, Any
from ast import Name, NodeTransformer
from tree.exceptions import FormulaError


class FormulaTransformer(NodeTransformer):
    """Validate an expression against registered keywords provided by the user."""
    def __init__(self, registered_kwargs: List[str]):
        self.registered_kwargs = registered_kwargs

    def visit_Name(self, node: Name) -> Any:
        if node.id not in self.registered_kwargs:
            raise FormulaError(f'Unregistered keyword: {node.id}')

        return node
