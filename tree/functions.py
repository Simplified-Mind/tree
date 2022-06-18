"""Functions"""


import pandas as pd
from typing import List, Union
from functools import reduce

__all__ = ['priority']


def priority(*args: List[Union[pd.DataFrame, pd.Series]]) -> Union[pd.DataFrame, pd.Series]:
    """"""
    return reduce(lambda l, r: l.combine_first(r), args)
