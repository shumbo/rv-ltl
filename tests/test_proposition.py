import pytest
from rv_ltl.b4 import B4
from rv_ltl.proposition import (
    Always,
    Atomic,
    And,
    Eventually,
    Implies,
    Next,
    Not,
    Or,
    Until,
)
from rv_ltl.exception import MissingAtomicsException


def test_trivial():
    ap1 = Atomic()
    m1 = ap1.create_monitor()
    m1.update({ap1: True})
    assert m1.evaluate() == B4.TRUE

    ap2 = Atomic()
    m2 = ap2.create_monitor()
    m2.update({ap2: False})
    assert m2.evaluate() == B4.FALSE


def test_update_by_id():
    phi = And(Atomic(identifier="alice"), Atomic(identifier="bob"))
    m = phi.create_monitor()
    m.update({"alice": True, "bob": True})
    assert m.evaluate() == B4.TRUE


def test_update_missing():
    ap1 = Atomic(name="atomic_proposition_1")
    m = ap1.create_monitor()
    with pytest.raises(MissingAtomicsException) as excinfo:
        m.update({})
    assert "atomic_proposition_1" in str(excinfo.value)


def test_update_missing_2():
    ap1 = Atomic(name="atomic_proposition_1")
    ap2 = Atomic()
    m = And(ap1, ap2).create_monitor()
    with pytest.raises(MissingAtomicsException) as excinfo:
        m.update({ap1: True})
    assert "1 unnamed atomic propotision" in str(excinfo.value)


def test_not():
    ap1 = Atomic()
    phi1 = Not(ap1)
    m1 = phi1.create_monitor()
    m1.update({ap1: True})
    assert m1.evaluate() == B4.FALSE

    ap2 = Atomic()
    phi2 = Not(ap2)
    m2 = phi2.create_monitor()
    m2.update({ap2: True})
    assert m2.evaluate() == B4.FALSE


def test_not_presumably_true():
    ap1 = Atomic()
    phi = Always(ap1)
    m = phi.create_monitor()
    m.update({ap1: True})
    assert m.evaluate() == B4.PRESUMABLY_TRUE


def test_not_presumably_false():
    ap1 = Atomic()
    phi = Eventually(ap1)
    m = phi.create_monitor()
    m.update({ap1: False})
    assert m.evaluate() == B4.PRESUMABLY_FALSE


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
    m = phi.create_monitor()
    m.update({ap1: v1, ap2: v2})
    assert m.evaluate() == expected


def test_and_vacuous():
    phi = And()
    m = phi.create_monitor()
    m.update({})
    assert m.evaluate() == B4.TRUE


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
    m = phi.create_monitor()
    m.update({ap1: v1, ap2: v2})
    assert m.evaluate() == expected


def test_or_vacuous():
    phi = Or()
    m = phi.create_monitor()
    m.update({})
    assert m.evaluate() == B4.FALSE


def test_next_1():
    ap1 = Atomic()
    m1 = Next(ap1).create_monitor()
    m1.update({ap1: True})
    m1.update({ap1: False})
    assert m1.evaluate() == B4.FALSE


def test_next_2():
    ap2 = Atomic()
    m2 = Next(ap2).create_monitor()
    m2.update({ap2: False})
    m2.update({ap2: True})
    assert m2.evaluate() == B4.TRUE


def test_next_3():
    ap3 = Atomic()
    m3 = Next(ap3).create_monitor()
    m3.update({ap3: True})
    assert m3.evaluate() == B4.PRESUMABLY_FALSE


def test_next_4():
    ap4 = Atomic()
    m4 = Next(ap4).create_monitor()
    assert m4.evaluate() == B4.PRESUMABLY_FALSE


def test_always_1():
    ap1 = Atomic()
    m = Always(ap1).create_monitor()
    for _ in range(10):
        m.update({ap1: True})
    assert m.evaluate() == B4.PRESUMABLY_TRUE


def test_always_2():
    ap1 = Atomic()
    m = Always(ap1).create_monitor()
    m.update({ap1: False})
    for _ in range(10):
        m.update({ap1: True})
    assert m.evaluate() == B4.FALSE


def test_until_1():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    m = phi.create_monitor()
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: True})
    assert m.evaluate() == B4.TRUE


def test_until_2():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    m = phi.create_monitor()
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: False, ap2: False})  # clearly violated here
    m.update({ap1: True, ap2: True})
    assert m.evaluate() == B4.FALSE


def test_until_3():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    m = phi.create_monitor()
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})  # ap2 can happen and phi can be satisfied
    assert m.evaluate() == B4.PRESUMABLY_FALSE


def test_until_4():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Until(ap1, ap2)  # ap1 until ap2
    m = phi.create_monitor()
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: True, ap2: False})
    m.update({ap1: False, ap2: True})  # ap1 can be false and still satisfied
    m.update({ap1: False, ap2: False})
    assert m.evaluate() == B4.TRUE


def test_eventually_1():
    ap1 = Atomic()
    phi = Eventually(ap1)
    m = phi.create_monitor()
    for _ in range(10):
        m.update({ap1: False})
    assert m.evaluate() == B4.PRESUMABLY_FALSE
    m.update({ap1: True})
    assert m.evaluate() == B4.TRUE


def test_implies_1():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Implies(ap1, ap2)
    m = phi.create_monitor()
    m.update({ap1: True, ap2: False})
    assert m.evaluate() == B4.FALSE


def test_implies_2():
    ap1 = Atomic()
    ap2 = Atomic()
    phi = Implies(ap1, ap2)
    m = phi.create_monitor()
    m.update({ap1: False, ap2: False})
    assert m.evaluate() == B4.TRUE


def test_request_response():
    request = Atomic(name="request")
    response = Atomic(name="response")
    # always (request -> eventually (response))
    phi = Always(Implies(request, Eventually(response)))
    m = phi.create_monitor()
    m.update({request: False, response: False})
    assert m.evaluate() == B4.PRESUMABLY_TRUE
    m.update({request: True, response: False})
    assert m.evaluate() == B4.PRESUMABLY_FALSE
    m.update({request: False, response: True})
    assert m.evaluate() == B4.PRESUMABLY_TRUE
