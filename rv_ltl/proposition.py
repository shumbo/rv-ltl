"Provide classes to compose RV-LTL formulae"

from typing import Union
from uuid import uuid4
from .monitor import (
    AlwaysMonitor,
    AndMonitor,
    EventuallyMonitor,
    ImpliesMonitor,
    Monitor,
    AtomicMonitor,
    NextMonitor,
    NotMonitor,
    OrMonitor,
    UntilMonitor,
)


class Proposition:
    def create_monitor(self) -> Monitor:
        """Using the proposition, create a monitor that can be used to evaluate a trace

        Returns:
            Monitor: A monitor for this proposition
        """
        raise NotImplementedError()


class Atomic(Proposition):
    def __init__(self, *, identifier: Union[str, None] = None, name="") -> None:
        """
        Construct an atomic proposition.

        Args:
            identifier: Identifier that can be used in `update`
            name: Name for the atomic proposition. Useful for debugging purposes.
        """
        super().__init__()
        self.identifier = identifier if identifier is not None else str(uuid4())
        self.name = name

    def create_monitor(self) -> Monitor:
        return AtomicMonitor(self)

    def __str__(self) -> str:
        # if name is specified, use it
        if self.name != "":
            return f"({self.name})"
        # otherwise, use the identifier
        return f"({self.identifier})"


class Not(Proposition):
    def __init__(self, op: Proposition) -> None:
        super().__init__()
        self.op = op

    def create_monitor(self) -> Monitor:
        return NotMonitor(self.op.create_monitor())


class And(Proposition):
    def __init__(self, *ops: Proposition) -> None:
        super().__init__()
        self.ops = ops

    def create_monitor(self) -> Monitor:
        return AndMonitor(*(op.create_monitor() for op in self.ops))


class Or(Proposition):
    def __init__(self, *ops: Proposition) -> None:
        super().__init__()
        self.ops = ops

    def create_monitor(self) -> Monitor:
        return OrMonitor(*(op.create_monitor() for op in self.ops))


class Next(Proposition):
    def __init__(self, op: Proposition) -> None:
        super().__init__()
        self.op = op

    def create_monitor(self) -> Monitor:
        return NextMonitor(self.op.create_monitor())


class Until(Proposition):
    def __init__(self, lhs: Proposition, rhs: Proposition) -> None:
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def create_monitor(self) -> Monitor:
        return UntilMonitor(self.lhs.create_monitor(), self.rhs.create_monitor())


class Eventually(Proposition):
    def __init__(self, op: Proposition) -> None:
        super().__init__()
        self.op = op

    def create_monitor(self) -> Monitor:
        return EventuallyMonitor(self.op.create_monitor())


class Always(Proposition):
    def __init__(self, op: Proposition) -> None:
        super().__init__()
        self.op = op

    def create_monitor(self) -> Monitor:
        return AlwaysMonitor(self.op.create_monitor())


class Implies(Proposition):
    def __init__(self, lhs: Proposition, rhs: Proposition) -> None:
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def create_monitor(self) -> Monitor:
        return ImpliesMonitor(self.lhs.create_monitor(), self.rhs.create_monitor())
