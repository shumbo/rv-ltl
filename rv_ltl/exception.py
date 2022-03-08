"Exceptions that are used across the package"

from typing import Set


class MissingAtomicsException(Exception):
    """
    raised when `update` is called with state that does not contain all atomic
    propositions on tree
    """

    def __init__(self, atomics: Set) -> None:
        super().__init__(atomics)
        self.atomics = atomics

    def __str__(self) -> str:
        names = []
        for ap in self.atomics:
            if ap.name != "":
                names.append(ap.name)
        unnamed_count = len(self.atomics) - len(names)
        s = "Missing atomic propositions: "
        s += ",".join(
            names
            + (
                [f"{unnamed_count} unnamed atomic propotision(s)"]
                if unnamed_count > 0
                else []
            )
        )
        return s
