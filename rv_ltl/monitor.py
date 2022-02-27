from functools import reduce
from operator import concat
from typing import Any, Dict, List, Set, Union
from rv_ltl.b4 import B4
from .exceptions import MissingAtomicsException

Step = Dict[Union[Any, str], bool]


class Monitor:
    def __init__(self) -> None:
        self._last_index = -1

    def update(self, step: Step):
        # get all atomic nodes on the tree
        nodes: Set["Monitor"] = set(self._flatten())
        atomic_monitors: Set[AtomicMonitor] = set(
            filter(lambda node: isinstance(node, AtomicMonitor), nodes)
        )
        atomic_propositions = {m.proposition for m in atomic_monitors}
        id_to_atomics = {ap.identifier: ap for ap in atomic_propositions}

        specified_atomics = set()
        instance_to_value = {}
        for k, v in step.items():
            if isinstance(k, str):
                instance = id_to_atomics.get(k)
            else:
                instance = k
            if instance is not None:
                specified_atomics.add(instance)
                instance_to_value[instance] = v

        missing = atomic_propositions.difference(specified_atomics)
        if len(missing) > 0:
            raise MissingAtomicsException(missing)
        for m in nodes:
            m._update_internal(instance_to_value)

    def evaluate(self) -> B4:
        """
        Evaluate the proposition with the current trace and get the result
        """
        return self._evaluate_at(0)

    def _flatten(self) -> List["Monitor"]:
        """
        Traverses the tree and return all nodes as a list
        """
        return [self]

    def _update_internal(self, m) -> None:
        self._last_index += 1

    def _evaluate_at(self, i: int = 0) -> B4:
        """
        Internal method for evaluating node starting at a given index

        Use `evaluate` for general use
        """
        raise NotImplementedError()

    def _is_future(self, t: int) -> bool:
        "Checks if the given `t` is in future"
        return t > self._last_index


# helper subclasses


class _UnaryMonitor(Monitor):
    """Monitor for unary operators

    implement `_evaluate_at`"""

    def __init__(self, op: Monitor) -> None:
        super().__init__()
        self.op = op

    def _flatten(self) -> List[Monitor]:
        return [self] + self.op._flatten()


class _VariadicMonitor(Monitor):
    """Monitor for operators with varying number of arguments

    implement `_evaluate_at`"""

    def __init__(self, *ops: Monitor) -> None:
        super().__init__()
        self.ops = ops

    def _flatten(self) -> List[Monitor]:
        return [self] + reduce(concat, [op._flatten() for op in self.ops], [])


class _BinaryMonitor(Monitor):
    """Monitor for operators with two arguments

    implement `_evaluate_at`"""

    def __init__(self, lhs: Monitor, rhs: Monitor) -> None:
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _flatten(self):
        return [self] + self.lhs._flatten() + self.rhs._flatten()


class _SyntacticSugarMonitor(_UnaryMonitor):
    """Monitor for operators that are syntactic sugar of other operators

    construct a new formula and pass it to `__init__`"""

    def __init__(self, evaluate_op: Monitor) -> None:
        super().__init__(evaluate_op)

    def _evaluate_at(self, i: int = 0) -> B4:
        return self.op._evaluate_at(i)


# constant monitors
class _ConstantTrueMonitor(Monitor):
    def _evaluate_at(self, i: int = 0) -> B4:
        return B4.TRUE


# monitor implementations


class AtomicMonitor(Monitor):
    def __init__(self, atomic_proposition) -> None:
        super().__init__()
        self.proposition = atomic_proposition
        self._history: List[bool] = []

    def _update_internal(self, m) -> None:
        super()._update_internal(m)
        v = m.get(self.proposition)
        if v is not None:
            self._history.append(v)

    def _evaluate_at(self, i: int = 0) -> B4:
        b = self._history[i]  # self.history[i:][0]
        b4 = B4.from_bool(b)
        return b4


class NotMonitor(_UnaryMonitor):
    def _evaluate_at(self, i=0) -> B4:
        v = ~self.op._evaluate_at(i)
        return v


class AndMonitor(_VariadicMonitor):
    def _evaluate_at(self, i=0) -> B4:
        values = [op._evaluate_at(i) for op in self.ops]
        v = reduce(lambda v1, v2: v1 & v2, values, B4.TRUE)
        return v


class OrMonitor(_VariadicMonitor):
    def _evaluate_at(self, i=0) -> B4:
        values = [op._evaluate_at(i) for op in self.ops]
        v = reduce(lambda v1, v2: v1 | v2, values, B4.FALSE)
        return v


class NextMonitor(_UnaryMonitor):
    def _evaluate_at(self, i=0) -> B4:
        next_i = i + 1
        # if it is the future
        v = None
        if self._is_future(next_i):
            # we cannot conclude a value
            # if it ends now, it is false
            v = B4.PRESUMABLY_FALSE
        # when next is called, children should only consider trace excluding the first
        else:
            v = self.op._evaluate_at(next_i)
        return v


class UntilMonitor(_BinaryMonitor):
    def _evaluate_at(self, i=0) -> B4:
        # look for time with rhs = True
        result = B4.FALSE
        for k in range(i, self._last_index + 1):
            v = self.rhs._evaluate_at(k)
            if not v.is_truthy:
                # if not is_truthy, try next k
                continue
            # truthy at k
            # check if lhs holds for all previous trace
            result = v  # if rhs is PRESUMABLY_TRUE, begin with it
            for j in range(i, min(i + k, self._last_index)):
                u = self.lhs._evaluate_at(j)
                result = result & u
            # take the best value among all k
            return result
        # if no k is found that satisfies rhs, return presumably false
        return B4.PRESUMABLY_FALSE


class EventuallyMonitor(_SyntacticSugarMonitor):
    def __init__(self, op: Monitor) -> None:
        super().__init__(UntilMonitor(_ConstantTrueMonitor(), op))


class AlwaysMonitor(_SyntacticSugarMonitor):
    def __init__(self, op: Monitor) -> None:
        super().__init__(NotMonitor(EventuallyMonitor(NotMonitor(op))))


class ImpliesMonitor(_SyntacticSugarMonitor):
    def __init__(self, lhs: Monitor, rhs: Monitor) -> None:
        super().__init__(OrMonitor(NotMonitor(lhs), rhs))
