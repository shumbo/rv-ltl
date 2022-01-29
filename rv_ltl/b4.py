from enum import unique, Enum


@unique
class B4(Enum):
    """
    B4 represents a four-value boolean used in RV-LTL
    """

    TRUE = 4
    PRESUMABLY_TRUE = 3
    PRESUMABLY_FALSE = 2
    FALSE = 1

    @staticmethod
    def from_bool(b: bool):
        "from_bool constructs a B4 from builtin bool type"
        return B4.TRUE if b else B4.FALSE

    @property
    def is_truthy(self) -> bool:
        "return True if the value is truthy (`TRUE` or `PRESUMABLY_TRUE`)"
        return self.value >= __class__.PRESUMABLY_TRUE.value

    @property
    def is_falsy(self) -> bool:
        "return False if the value is falsy (`FALSE` or `PRESUMABLY_FALSE`)"
        return self.value <= __class__.PRESUMABLY_FALSE.value

    def __bool__(self):
        raise NotImplementedError("Do not use bool() on B4")

    def __invert__(self):
        return __class__(5 - self.value)

    def __and__(self, value):
        return __class__(min(self.value, value.value))

    def __or__(self, value):
        return __class__(max(self.value, value.value))

    def __str__(self):
        if self == __class__.TRUE:
            return "TRUE"
        if self == __class__.PRESUMABLY_TRUE:
            return "PRESUMABLY_TRUE"
        if self == __class__.PRESUMABLY_FALSE:
            return "PRESUMABLY_FALSE"
        if self == __class__.FALSE:
            return "FALSE"
        return "unknown"
