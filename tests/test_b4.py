import pytest
from rv_ltl.b4 import B4


@pytest.mark.parametrize(
    "v1, v2, expected",
    [
        (B4.TRUE, B4.TRUE, B4.TRUE),
        (B4.TRUE, B4.PRESUMABLY_TRUE, B4.PRESUMABLY_TRUE),
        (B4.TRUE, B4.PRESUMABLY_FALSE, B4.PRESUMABLY_FALSE),
        (B4.TRUE, B4.FALSE, B4.FALSE),
        (B4.PRESUMABLY_TRUE, B4.PRESUMABLY_TRUE, B4.PRESUMABLY_TRUE),
        (B4.PRESUMABLY_TRUE, B4.PRESUMABLY_FALSE, B4.PRESUMABLY_FALSE),
        (B4.PRESUMABLY_TRUE, B4.FALSE, B4.FALSE),
        (B4.PRESUMABLY_FALSE, B4.PRESUMABLY_FALSE, B4.PRESUMABLY_FALSE),
        (B4.PRESUMABLY_FALSE, B4.FALSE, B4.FALSE),
        (B4.FALSE, B4.FALSE, B4.FALSE),
    ],
)
def test_and(v1, v2, expected):
    assert v1 & v2 == expected


@pytest.mark.parametrize(
    "v1, v2, expected",
    [
        (B4.TRUE, B4.TRUE, B4.TRUE),
        (B4.TRUE, B4.PRESUMABLY_TRUE, B4.TRUE),
        (B4.TRUE, B4.PRESUMABLY_FALSE, B4.TRUE),
        (B4.TRUE, B4.FALSE, B4.TRUE),
        (B4.PRESUMABLY_TRUE, B4.PRESUMABLY_TRUE, B4.PRESUMABLY_TRUE),
        (B4.PRESUMABLY_TRUE, B4.PRESUMABLY_FALSE, B4.PRESUMABLY_TRUE),
        (B4.PRESUMABLY_TRUE, B4.FALSE, B4.PRESUMABLY_TRUE),
        (B4.PRESUMABLY_FALSE, B4.PRESUMABLY_FALSE, B4.PRESUMABLY_FALSE),
        (B4.PRESUMABLY_FALSE, B4.FALSE, B4.PRESUMABLY_FALSE),
        (B4.FALSE, B4.FALSE, B4.FALSE),
    ],
)
def test_or(v1, v2, expected):
    assert v1 | v2 == expected


@pytest.mark.parametrize(
    "v, expected",
    [
        (B4.TRUE, B4.FALSE),
        (B4.PRESUMABLY_TRUE, B4.PRESUMABLY_FALSE),
        (B4.PRESUMABLY_FALSE, B4.PRESUMABLY_TRUE),
        (B4.FALSE, B4.TRUE),
    ],
)
def test_not(v, expected):
    assert ~v == expected
