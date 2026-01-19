from typing import Any

from qoala.types.quantum.qubit import Qubit


class ScopedVar:
    # TODO - Implement this class
    def assign(self, expr: Any):
        pass


# We inherit from Qubit, so this class behaves as a qubit. In this way,
# the IDE does not complain about "unknown methods" (like X(), measure(), etc.)
class ScopedQubit(Qubit):
    # TODO - Implement this class
    def __init__(self, qubit: Qubit):
        pass
