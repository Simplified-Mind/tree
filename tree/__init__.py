"""
## User case
It aims to reduce the complexities when building reactive business intelligences.

## Core concept
Each node represents a pd.Series and can be associated with an expression, which will be validated and evaluated
dynamically.
"""

from tree.node import Node, SymlinkNode
