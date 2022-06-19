"""Exception/Warning to inspect formula and node construction."""


class FormulaError(RuntimeError):
    """Prevent arbitrary formula to be executed on demand."""
    pass


class MissingFormula(RuntimeWarning):
    """Issue warning at the pointing of calculation if formula is missing."""
    pass


class ReadOnlyError(RuntimeError):
    """Prevent children to be modified."""
    pass

