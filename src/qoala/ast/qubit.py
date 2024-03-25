from abc import ABC
from typing import Self

import qnet.dialects.qnet as qnet
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaNumericValue, ImmediateQIntOrExpression, ImmediateQFloatOrExpression


class QoalaQubit(QoalaExpression, ABC):
    pass


class QoalaLocalQubit(QoalaQubit):
    def __init__(self):
        super().__init__()
        QoalaProgram.add_to_body(self)

    def measure(self) -> QoalaOperation:
        # When we measure, _at runtime_ we get a value of type Bit (or QoalaBit).
        # However, here we need to model how the measure operation is compiled
        # Being this said, we need to return a "QubitMeasure" operation
        from qoala.ast.operations.quantum import QubitMeasure
        # TODO - Do we need to specify the base?
        return QubitMeasure(self)

    def X(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import XGate
        return QoalaOperation._create_expression_for_op(XGate, self)

    def Y(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import YGate
        return QoalaOperation._create_expression_for_op(YGate, self)

    def Z(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import ZGate
        return QoalaOperation._create_expression_for_op(ZGate, self)

    def T(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import TGate
        return QoalaOperation._create_expression_for_op(TGate, self)

    def H(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import HGate
        return QoalaOperation._create_expression_for_op(HGate, self)

    def K(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import KGate
        return QoalaOperation._create_expression_for_op(KGate, self)

    def S(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import SGate
        return QoalaOperation._create_expression_for_op(SGate, self)

    def rot_X(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        if isinstance(n, int):
            n_val = QoalaNumericValue.from_immediate(n)
        else:
            n_val = n
        if isinstance(d, int):
            d_val = QoalaNumericValue.from_immediate(d)
        else:
            d_val = d
        if angle is None:
            angle_val = QoalaNumericValue.from_immediate(0.0)
        elif isinstance(angle, float):
            angle_val = QoalaNumericValue.from_immediate(angle)
        else:
            angle_val = angle
        from qoala.ast.operations.quantum import RotateX
        return QoalaOperation._create_expression_for_op(RotateX, qubit=self, n=n_val, d=d_val, angle=angle_val)

    def rot_Y(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        if isinstance(n, int):
            n_val = QoalaNumericValue.from_immediate(n)
        else:
            n_val = n
        if isinstance(d, int):
            d_val = QoalaNumericValue.from_immediate(d)
        else:
            d_val = d
        if angle is None:
            angle_val = QoalaNumericValue.from_immediate(0.0)
        elif isinstance(angle, float):
            angle_val = QoalaNumericValue.from_immediate(angle)
        else:
            angle_val = angle
        from qoala.ast.operations.quantum import RotateY
        return QoalaOperation._create_expression_for_op(RotateY, qubit=self, n=n_val, d=d_val, angle=angle_val)

    def rot_Z(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        if isinstance(n, int):
            n_val = QoalaNumericValue.from_immediate(n)
        else:
            n_val = n
        if isinstance(d, int):
            d_val = QoalaNumericValue.from_immediate(d)
        else:
            d_val = d
        if angle is None:
            angle_val = QoalaNumericValue.from_immediate(0.0)
        elif isinstance(angle, float):
            angle_val = QoalaNumericValue.from_immediate(angle)
        else:
            angle_val = angle
        from qoala.ast.operations.quantum import RotateZ
        return QoalaOperation._create_expression_for_op(RotateZ, qubit=self, n=n_val, d=d_val, angle=angle_val)

    def cnot(self, target: Self) -> QoalaOperation:
        from qoala.ast.operations.quantum import CNotGate
        return QoalaOperation._create_expression_for_op(CNotGate, qubit=self, target=target)

    def cphase(self, target: Self) -> QoalaOperation:
        from qoala.ast.operations.quantum import CPhaseGate
        return QoalaOperation._create_expression_for_op(CPhaseGate, target=target)

    def reset(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import QubitReset
        return QoalaOperation._create_expression_for_op(QubitReset, self)

    def free(self) -> QoalaOperation:
        # TODO - Implement
        pass

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self.hir = qnet.new_qubit()
        return self.hir


# TODO - Implement remote qubits
class QoalaRemoteQubit(QoalaQubit):
    pass
