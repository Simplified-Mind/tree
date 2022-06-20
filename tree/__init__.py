"""
## Goal
It aims to reduce the complexities when building reactive business intelligences.

## Pain points of the current approach
Any change to the model involves many moving components and resources demanding.

## Core concepts of the proposed approach
- Each node represents a timeseries and can be associated with an expression, which will be validated and evaluated
dynamically.
- Bottom up approach, the child node can be set as the trigger node resulting in the recalculation of the parent nodes automatically.
- Updates a child (leaf or aggregated level) that is linked to multiple parents, the entire system could be updated
from the child above.
"""

from tree.node import Node, SymlinkNode
from tree.exceptions import FormulaError, MissingFormula, ReadOnlyError
from tree.functions import *
from tree.utils import FormulaTransformer
