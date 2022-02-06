from functools import reduce
import operator
from typing import Dict, List, Set
from uuid import uuid4

from rv_ltl.b4 import B4


State = Dict["Atomic", bool]


class MissingAtomicsException(Exception):
    """
    raised when `update` is called with state that does not contain all atomic
    propositions on tree
    """

    def __init__(self, atomics: Set["Atomic"]) -> None:
        super().__init__(atomics)
        self.atomics = atomics

    def __str__(self) -> str:
        names = []
        for ap in self.atomics:
            if ap.name is not None and ap.name != "":
                names.append(ap.name)
        unnamed_count = len(self.atomics) - len(names)
        s = "Missing atomic propositions: "
        s += ",".join(
            [",".join(names), f"{unnamed_count} unnamed atomic propotision(s)"]
        )
        return s


class Node:
    def __init__(self) -> None:
        self._last_index = -1
        "the last index of the history list"

    def is_future(self, t: int) -> bool:
        "Checks if the given `t` is in future"
        return t > self._last_index

    def update(self, m: State) -> None:
        """
        Accept all children nodes with a new state

        Pass a state as a map from atomic propositions to booleans
        You must pass all atomic propositions under the node

        Raises `MissingAtomicsException` if some atomic propositions are missing
        """
        # get all atomic nodes on the tree
        nodes: Set["Node"] = set(self._flatten())
        atomics = set(filter(lambda node: isinstance(node, Atomic), nodes))

        # get all atomics nodes specified in the given state
        specified_atomics = set(m.keys())

        # raise an error if there is a missing atomic proposition
        missing = atomics.difference(specified_atomics)
        if len(missing) > 0:
            raise MissingAtomicsException(missing)

        # call _internal_update on each node
        for node in nodes:
            node._update_internal(m)

    def _update_internal(self, m: State) -> None:
        self._last_index += 1

    def _flatten(self) -> List["Node"]:
        """
        Traverses the tree and return all nodes as a list
        """
        return [self]

    def _evaluate_at(self, i: int = 0) -> B4:
        """
        Internal method for evaluating node starting at a given index

        Use `evaluate` for general use
        """
        raise NotImplementedError()

    def evaluate(self) -> B4:
        """
        Evaluate the formula and get the result

        t specifies the time to evaluate
        i specifies where to start the trace (default: 0)
        """
        return self._evaluate_at(0)


class ConstantTrue(Node):
    def _evaluate_at(self, i=0) -> B4:
        return B4.TRUE

    def __str__(self) -> str:
        return "⊤"


class ConstantFalse(Node):
    def _evaluate_at(self, i=0) -> B4:
        return B4.FALSE

    def __str__(self) -> str:
        return "⊥"


class Atomic(Node):
    def __init__(self, name="") -> None:
        super().__init__()
        self.name = name
        self.id = uuid4()
        self.history: List[bool] = list()

    def _update_internal(self, m: State) -> None:
        super()._update_internal(m)
        for k, v in m.items():
            if k is self:
                self.history.append(v)

    def _evaluate_at(self, i=0) -> B4:
        b = self.history[i]  # self.history[i:][0]
        b4 = B4.from_bool(b)
        return b4

    def __str__(self) -> str:
        return self.name


class Not(Node):
    def __init__(self, op: Node) -> None:
        super().__init__()
        self.op = op

    def _flatten(self):
        return [self] + self.op._flatten()

    def _evaluate_at(self, i=0) -> B4:
        v = ~self.op._evaluate_at(i)
        return v

    def __str__(self) -> str:
        return f"(¬{str(self.op)})"


class And(Node):
    def __init__(self, *ops: Node) -> None:
        super().__init__()
        self.ops = ops

    def _flatten(self):
        return [self] + reduce(operator.concat, [op._flatten() for op in self.ops])

    def _evaluate_at(self, i=0) -> B4:
        values = [op._evaluate_at(i) for op in self.ops]
        v = reduce(lambda v1, v2: v1 & v2, values)
        return v

    def __str__(self) -> str:
        return "(" + " ∧ ".join([f"({str(op)})" for op in self.ops]) + ")"


class Or(Node):
    def __init__(self, *ops: Node) -> None:
        super().__init__()
        self.ops = ops

    def _flatten(self):
        return [self] + reduce(operator.concat, [op._flatten() for op in self.ops])

    def _evaluate_at(self, i=0) -> B4:
        values = [op._evaluate_at(i) for op in self.ops]
        v = reduce(lambda v1, v2: v1 | v2, values)
        return v

    def __str__(self) -> str:
        return "(" + " ∨ ".join([f"({str(op)})" for op in self.ops]) + ")"


class Next(Node):
    def __init__(self, op: Node):
        super().__init__()
        self.op = op

    def _flatten(self):
        return [self] + self.op._flatten()

    def _evaluate_at(self, i=0) -> B4:
        next_i = i + 1
        # if it is the future
        v = None
        if self.is_future(next_i):
            # we cannot conclude a value
            # if it ends now, it is false
            v = B4.PRESUMABLY_FALSE
        # when next is called, children should only consider trace excluding the first
        else:
            v = self.op._evaluate_at(next_i)
        return v

    def __str__(self) -> str:
        return f"(X({str(self.op)}))"


class Until(Node):
    def __init__(self, lhs: Node, rhs: Node) -> None:
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def _flatten(self):
        return [self] + self.lhs._flatten() + self.rhs._flatten()

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

    def __str__(self) -> str:
        return f"({str(self.lhs)} U {str(self.rhs)})"


class Eventually(Node):
    def __init__(self, op: Node) -> None:
        super().__init__()
        self.original = op
        self.op = Until(ConstantTrue(), op)

    def _flatten(self) -> List["Node"]:
        return [self] + self.op._flatten()

    def _evaluate_at(self, i=0) -> B4:
        v = self.op._evaluate_at(i)
        return v

    def __str__(self) -> str:
        return f"(eventually {str(self.original)})"


class Always(Node):
    def __init__(self, op: Node) -> None:
        super().__init__()
        self.original = op
        self.op = Not(Eventually(Not(op)))

    def _flatten(self) -> List["Node"]:
        return [self] + self.op._flatten()

    def _evaluate_at(self, i=0) -> B4:
        v = self.op._evaluate_at(i)
        return v

    def __str__(self) -> str:
        return f"(always {str(self.original)})"


class Implies(Node):
    def __init__(self, lhs: Node, rhs: Node) -> None:
        super().__init__()
        self.original_lhs = lhs
        self.original_rhs = rhs
        self.op = Or(Not(lhs), rhs)

    def _flatten(self):
        return [self] + self.op._flatten()

    def _evaluate_at(self, i=0) -> B4:
        v = self.op._evaluate_at(i)
        return v

    def __str__(self) -> str:
        return f"({str(self.original_lhs)} implies {str(self.original_rhs)})"
