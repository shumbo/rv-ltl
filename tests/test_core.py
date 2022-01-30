import pytest
from rv_ltl.b4 import B4
from rv_ltl.core import (
    Always,
    Atomic,
    Eventually,
    Implies,
    Next,
    Not,
    And,
    Or,
    Until,
)


def test_trivial():
    ap1 = Atomic()
    ap1.update({ap1: True})
    assert ap1.evaluate() == B4.TRUE

    ap2 = Atomic()
    ap2.update({ap2: False})
    assert ap2.evaluate() == B4.FALSE


def test_time():
    ap1 = Atomic()
    ap1.update({ap1: True})
    ap1.update({ap1: True})
    ap1.update({ap1: False})
    assert ap1.evaluate(0) == B4.TRUE
    assert ap1.evaluate(1) == B4.TRUE
    assert ap1.evaluate(2) == B4.FALSE


def test_not():
    ap1 = Atomic()
    phi = Not(ap1)
    phi.update({ap1: True})
    phi.update({ap1: False})
    assert phi.evaluate(0) == B4.FALSE
    assert phi.evaluate(1) == B4.TRUE


def test_not_presumably_true():
    ap1 = Atomic()
    phi = Always(ap1)
    phi.update({ap1: True})
    assert phi.evaluate() == B4.PRESUMABLY_TRUE


def test_not_presumably_false():
    ap1 = Atomic()
    phi = Eventually(ap1)
    phi.update({ap1: False})
    assert phi.evaluate() == B4.PRESUMABLY_FALSE


@pytest.mark.parametrize(
    "v1, v2, expected",
    [
        (True, True, B4.TRUE),
        (True, False, B4.FALSE),
        (False, True, B4.FALSE),
        (False, False, B4.FALSE),
    ],
)
def test_and(v1, v2, expected):
    ap1 = Atomic()
    ap2 = Atomic()
    phi = And(ap1, ap2)
    phi.update({ap1: v1, ap2: v2})
    assert phi.evaluate(0) == expected


@pytest.mark.parametrize(
    "v1, v2, expected",
    [
        (True, True, B4.TRUE),
        (True, False, B4.TRUE),
        (False, True, B4.TRUE),
        (False, False, B4.FALSE),
    ],
)
def test_or(v1, v2, expected):
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Or(ap1, ap2)
    phi.update({ap1: v1, ap2: v2})
    assert phi.evaluate(0) == expected


def test_next():
    ap1 = Atomic()
    phi = Next(ap1)
    phi.update({ap1: True})
    phi.update({ap1: False})
    phi.update({ap1: True})
    assert phi.evaluate(0) == B4.FALSE
    assert phi.evaluate(1) == B4.TRUE
    assert phi.evaluate(2) == B4.PRESUMABLY_FALSE


def test_always_1():
    ap1 = Atomic()
    phi = Always(ap1)
    for _ in range(10):
        phi.update({ap1: True})
    assert phi.evaluate() == B4.PRESUMABLY_TRUE


def test_always_2():
    ap1 = Atomic()
    phi = Always(ap1)
    phi.update({ap1: False})
    for _ in range(10):
        phi.update({ap1: True})
    assert phi.evaluate() == B4.FALSE


def test_until_1():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: True})
    assert phi.evaluate() == B4.TRUE


def test_until_2():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: False, ap2: False})  # clearly violated here
    phi.update({ap1: True, ap2: True})
    assert phi.evaluate() == B4.FALSE


def test_until_3():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})  # ap2 can happen and phi can be satisfied
    assert phi.evaluate() == B4.PRESUMABLY_FALSE


def test_until_4():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: True, ap2: False})
    phi.update({ap1: False, ap2: True})  # ap1 can be false and still satisfied
    phi.update({ap1: False, ap2: False})
    assert phi.evaluate() == B4.TRUE


def test_eventually_1():
    ap1 = Atomic()
    phi = Eventually(ap1)
    for _ in range(10):
        phi.update({ap1: False})
    assert phi.evaluate() == B4.PRESUMABLY_FALSE
    phi.update({ap1: True})
    assert phi.evaluate() == B4.TRUE


def test_implies_1():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Implies(ap1, ap2)
    phi.update({ap1: True, ap2: False})
    assert phi.evaluate() == B4.FALSE


def test_implies_2():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Implies(ap1, ap2)
    phi.update({ap1: False, ap2: False})
    assert phi.evaluate() == B4.TRUE


def test_request_response():
    request = Atomic("request")
    response = Atomic("request")
    # always (request -> eventually (response))
    phi = Always(Implies(request, Eventually(response)))
    phi.update({request: False, response: False})
    assert phi.evaluate() == B4.PRESUMABLY_TRUE
    phi.update({request: True, response: False})
    assert phi.evaluate() == B4.PRESUMABLY_FALSE
    phi.update({request: False, response: True})
    assert phi.evaluate() == B4.PRESUMABLY_TRUE
