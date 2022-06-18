"""Utility"""


from typing import List, Any
from ast import Name, NodeTransformer
from tree.exceptions import FormulaError


class FormulaTransformer(NodeTransformer):
    def __init__(self, registered_kwargs: List[str]):
        self.registered_kwargs = registered_kwargs

    def visit_Name(self, node: Name) -> Any:
        if node.id not in self.registered_kwargs:
            raise FormulaError('Please use registered functions with correct variable names from the children')

        return node
