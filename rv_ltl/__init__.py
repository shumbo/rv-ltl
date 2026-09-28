"""
`rv-ltl` is a Python package that implements
Runtime Verification Linear Temporal Logic (RV-LTL).


.. include:: ./README.md
"""

from importlib.metadata import version as _version

__version__ = _version("rv-ltl")

from .b4 import B4
from .proposition import (
    Atomic,
    Not,
    And,
    Or,
    Next,
    Until,
    Eventually,
    Always,
    Implies,
)
from .exception import MissingAtomicsException
from .monitor import Monitor
