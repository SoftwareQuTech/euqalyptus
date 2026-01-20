from typing import Any

from qoala.ast.model import QoalaRuntimeValue
from qoala.types.classical import NumericOperandsOverload, BooleanOperandsOverload
from qoala.types.quantum.qubit import Qubit


class ScopedVar(NumericOperandsOverload, BooleanOperandsOverload):
    # TODO - Implement this class
    def __new__(cls):
        return QoalaRuntimeValue()

    def __init__(self):
        # Nothing to do here
        pass

    def assign(self, value: Any):
        # Nothing to do here
        pass


# We inherit from Qubit, so this class behaves as a qubit. In this way,
# the IDE does not complain about "unknown methods" (like X(), measure(), etc.)
class ScopedQubit(Qubit):
    # TODO - Implement this class
    def __init__(self, qubit: Qubit):
        pass
