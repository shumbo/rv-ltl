"""
`rv-ltl` is a Python package that implements
Runtime Verification Linear Temporal Logic (RV-LTL).


.. include:: ./README.md
"""

__version__ = "0.1.0a1"

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
