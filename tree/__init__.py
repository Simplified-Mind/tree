"""
## User case
It aims to reduce the complexities when building reactive business intelligences.

## Core concept
- Each node represents a pd.Series and can be associated with an expression, which will be validated and evaluated
dynamically.
- Bottom up approach for the system updates, i.e., children can be set to trigger the recalculation of the parent automatically.
- Updates a child (leaf or aggregated level) that is linked to multiple parents, the entire system could be updated
from the child above.
"""

from tree.node import Node, SymlinkNode
from tree.exceptions import FormulaError, MissingFormula, ReadOnlyError
from tree.functions import *
from tree.utils import FormulaTransformer
