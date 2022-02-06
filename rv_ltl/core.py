from functools import reduce
from typing import Dict, List
from uuid import uuid4

from rv_ltl.b4 import B4


State = Dict["Atomic", bool]


class Node:
    def __init__(self) -> None:
        self.last_index = -1
        "the last index of the history list"

    def is_future(self, t: int) -> bool:
        "Checks if the given `t` is in future"
        return t > self.last_index

    def update(self, m: State) -> None:
        self.last_index += 1

    def _evaluate_at(self, i: int = 0) -> B4:
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

    def update(self, m: State) -> None:
        super().update(m)
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

    def update(self, m: State) -> None:
        super().update(m)
        self.op.update(m)

    def _evaluate_at(self, i=0) -> B4:
        v = ~self.op._evaluate_at(i)
        return v

    def __str__(self) -> str:
        return f"(¬{str(self.op)})"


class And(Node):
    def __init__(self, *ops: Node) -> None:
        super().__init__()
        self.ops = ops

    def update(self, m: State) -> None:
        super().update(m)
        for op in self.ops:
            op.update(m)

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

    def update(self, m: State) -> None:
        super().update(m)
        for op in self.ops:
            op.update(m)

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

    def update(self, m: State) -> None:
        super().update(m)
        self.op.update(m)

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

    def update(self, m: State) -> None:
        super().update(m)
        self.lhs.update(m)
        self.rhs.update(m)

    def _evaluate_at(self, i=0) -> B4:
        # look for time with rhs = True
        result = B4.FALSE
        for k in range(i, self.last_index + 1):
            v = self.rhs._evaluate_at(k)
            if not v.is_truthy:
                # if not is_truthy, try next k
                continue
            # truthy at k
            # check if lhs holds for all previous trace
            result = v  # if rhs is PRESUMABLY_TRUE, begin with it
            for j in range(i, min(i + k, self.last_index)):
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

    def update(self, m: State) -> None:
        super().update(m)
        self.op.update(m)

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

    def update(self, m: State) -> None:
        super().update(m)
        self.op.update(m)

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

    def update(self, m: State) -> None:
        super().update(m)
        self.op.update(m)

    def _evaluate_at(self, i=0) -> B4:
        v = self.op._evaluate_at(i)
        return v

    def __str__(self) -> str:
        return f"({str(self.original_lhs)} implies {str(self.original_rhs)})"
