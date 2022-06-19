"""Functions are designed to handle pre-defined data manipulation.

Examples:
    >>> from tree import priority
    >>> import pandas as pd
    >>> priority(pd.Series(range(1)), pd.Series(range(2)), pd.Series(range(3)))
    Out[11]:
    0    0.0
    1    1.0
    2    2.0
    dtype: float64

The module contains the following classes/functions:

- `priority(*args: List[Union[pd.DataFrame, pd.Series]]) -> Union[pd.DataFrame, pd.Series]`
"""


import pandas as pd
from typing import List, Union
from functools import reduce

__all__ = ['priority']


def priority(*args: List[Union[pd.DataFrame, pd.Series]]) -> Union[pd.DataFrame, pd.Series]:
    """Pandas combine_first for multiple DataFrame/Series."""
    return reduce(lambda l, r: l.combine_first(r), args)
