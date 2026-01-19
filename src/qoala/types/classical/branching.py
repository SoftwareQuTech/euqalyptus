from typing import Any

from qoala.ast.operations import with_arith_operators, with_bool_operators, with_order_operators
from qoala.ast.value import QoalaInteger, QoalaBool, QoalaFloat
from qoala.types.quantum.qubit import Qubit


@with_arith_operators
@with_bool_operators
@with_order_operators
class ScopedVar:
    # TODO - Implement this class
    def __init__(self):
        # No debug info needed for this class, but we need this field
        # to correctly process the AST
        self.debug_info = None

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaInteger or cls == QoalaBool or cls == QoalaFloat

    def assign(self, expr: Any):
        pass


# We inherit from Qubit, so this class behaves as a qubit. In this way,
# the IDE does not complain about "unknown methods" (like X(), measure(), etc.)
class ScopedQubit(Qubit):
    # TODO - Implement this class
    def __init__(self, qubit: Qubit):
        pass
