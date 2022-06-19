"""
## User case
It aims to reduce the complexities when building reactive business intelligences.

## Core concept
- Each node represents a pd.Series and can be associated with an expression, which will be validated and evaluated
dynamically.
- Parent (not root) is updated by the children, i.e., bottom up approach.
- Updates a child (leaf or aggregated level) that is linked to multiple parents, the entire system could be updated
from the child above.
"""

from tree.node import Node, SymlinkNode
from tree.exceptions import FormulaError, MissingFormula, ReadOnlyError
from tree.functions import *
from tree.utils import FormulaTransformer
