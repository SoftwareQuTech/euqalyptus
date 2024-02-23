from typing import Self

from qoala import QoalaProgram
from qoala.ast import QoalaExpression, QoalaOperation
from qoala.ast.value import QoalaInteger, QoalaFloat


class QoalaQubit(QoalaExpression):
    pass


class QoalaLocalQubit(QoalaQubit):
    def __init__(self):
        QoalaProgram.add_to_body(self)

    def measure(self) -> QoalaOperation:
        # When we measure, _at runtime_ we get a value of type Bit (or QoalaBit).
        # However, here we need to model how the measure operation is compiled
        # Being this said, we need to return a "QubitMeasure" operation
        from qoala.ast.operations.quantum import QubitMeasure
        # TODO - Do we need to specify the base?
        return QubitMeasure(self)

    def X(self):
        from qoala.ast.operations.quantum import XGate
        return QoalaOperation._create_expression_for_op(XGate, self)

    def Y(self):
        from qoala.ast.operations.quantum import YGate
        return QoalaOperation._create_expression_for_op(YGate, self)

    def Z(self):
        from qoala.ast.operations.quantum import ZGate
        return QoalaOperation._create_expression_for_op(ZGate, self)

    def T(self):
        from qoala.ast.operations.quantum import TGate
        return QoalaOperation._create_expression_for_op(TGate, self)

    def H(self):
        from qoala.ast.operations.quantum import HGate
        return QoalaOperation._create_expression_for_op(HGate, self)

    def K(self):
        from qoala.ast.operations.quantum import KGate
        return QoalaOperation._create_expression_for_op(KGate, self)

    def S(self):
        from qoala.ast.operations.quantum import SGate
        return QoalaOperation._create_expression_for_op(SGate, self)

    def rot_X(
            self,
            n: int | QoalaInteger = 0,
            d: int | QoalaInteger = 0,
            angle: float | QoalaFloat | None = None
    ):
        # TODO - Implement
        pass

    def rot_Y(
            self,
            n: int | QoalaInteger = 0,
            d: int | QoalaInteger = 0,
            angle: float | QoalaFloat | None = None
    ):
        # TODO - Implement
        pass

    def rot_Z(
            self,
            n: int | QoalaInteger = 0,
            d: int | QoalaInteger = 0,
            angle: float | QoalaFloat | None = None
    ):
        # TODO - Implement
        pass

    def cnot(self, target: Self) -> None:
        # TODO - Implement
        pass

    def cphase(self, target: Self) -> None:
        # TODO - Implement
        pass

    def reset(self) -> None:
        # TODO - Implement
        pass

    def free(self) -> None:
        # TODO - Implement
        pass


# TODO - Implement remote qubits
class QoalaRemoteQubit(QoalaQubit):
    pass
