import math
from abc import ABC, abstractmethod
from typing import Self

import qnet.dialects.qnet as qnet
import qnet.dialects.tensor as tensor
from qnet.dialects.qnet import QubitType
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import (
    QoalaNumericValue,
    ImmediateQIntOrExpression,
    ImmediateQFloatOrExpression,
    QoalaFloatOrExpression
)


class QoalaQubit(QoalaExpression, ABC):
    @abstractmethod
    def measure(self) -> QoalaOperation:
        pass

    @abstractmethod
    def X(self) -> QoalaOperation:
        pass

    @abstractmethod
    def Y(self) -> QoalaOperation:
        pass

    @abstractmethod
    def Z(self) -> QoalaOperation:
        pass

    @abstractmethod
    def T(self) -> QoalaOperation:
        pass

    @abstractmethod
    def H(self) -> QoalaOperation:
        pass

    @abstractmethod
    def K(self) -> QoalaOperation:
        pass

    @abstractmethod
    def S(self) -> QoalaOperation:
        pass

    @staticmethod
    def _process_angles(
            n: ImmediateQIntOrExpression | None = None,
            d: ImmediateQIntOrExpression | None = None,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> ImmediateQFloatOrExpression:
        # if n and d are immediates, then we can directly compute the value of angle
        if n is not None and d is not None:
            # In this case, we know that n and d are given
            if isinstance(n, int) and isinstance(d, int):
                # angle can be computed at compile time
                angle_val = float(n * math.pi / (math.pow(2, n)))
            else:
                # n and d are given, but, at least, one of them is not an immediate -> angle is known at runtime
                if isinstance(n, int):
                    n_val = QoalaNumericValue.from_immediate(n)
                else:
                    n_val = n
                if isinstance(d, int):
                    d_val = QoalaNumericValue.from_immediate(d)
                else:
                    d_val = d
                # angle_val = (n * \pi) / 2 ** d, this means:
                # $pi = arith.const 3.14 : f32
                # $n_f32 = arith.uitofp $n : f32
                # $up = arith.mulf $n_f32, $pi : f32
                # $down = math.exp2 $d : f32 ;; convenient base-2 exponentiation operation
                # $angle_val = arith.divf $up, $down : f32
                # TODO - Implement this
                angle_val = None
        else:
            # In this case, either n and/or d were not given; we rely on the angle
            if isinstance(angle, float):
                # Angle was given as an immediate
                angle_val = QoalaNumericValue.from_immediate(angle)
            elif isinstance(angle, QoalaFloatOrExpression):
                # Angle can be evaluated at runtime
                angle_val = angle
            else:
                # Worst-worst case... we have nothing
                angle_val = QoalaNumericValue.from_immediate(0.0)
        return angle_val

    @abstractmethod
    def rot_X(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        pass

    @abstractmethod
    def rot_Y(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        pass

    @abstractmethod
    def rot_Z(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        pass

    @abstractmethod
    def cnot(self, target: Self) -> QoalaOperation:
        pass

    @abstractmethod
    def cphase(self, target: Self) -> QoalaOperation:
        pass

    @abstractmethod
    def reset(self) -> QoalaOperation:
        pass

    @abstractmethod
    def free(self) -> QoalaOperation:
        # TODO - Implement
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
        angle_val = QoalaLocalQubit._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateX
        return QoalaOperation._create_expression_for_op(RotateX, qubit=self, angle=angle_val)

    def rot_Y(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QoalaLocalQubit._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateY
        return QoalaOperation._create_expression_for_op(RotateY, qubit=self, angle=angle_val)

    def rot_Z(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QoalaLocalQubit._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateZ
        return QoalaOperation._create_expression_for_op(RotateZ, qubit=self, angle=angle_val)

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

    def to_ir(self, ctx: Context):
        self.ir = qnet.new_qubit()
        return self.ir


# TODO - Implement remote qubits
class QoalaRemoteQubit(QoalaQubit):
    def __init__(self, name: str, n: int):
        super().__init__()
        self.name = name
        self.n = n
        QoalaProgram.add_to_body(self)

    #  TODO - Do the remote qubits support the same operations and local?
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
        angle_val = QoalaLocalQubit._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateX
        return QoalaOperation._create_expression_for_op(RotateX, qubit=self, angle=angle_val)

    def rot_Y(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QoalaLocalQubit._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateY
        return QoalaOperation._create_expression_for_op(RotateY, qubit=self, angle=angle_val)

    def rot_Z(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QoalaLocalQubit._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateZ
        return QoalaOperation._create_expression_for_op(RotateZ, qubit=self, angle=angle_val)

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

    # Functions for generating IR
    def can_evaluate_to(self, cls) -> bool:
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # Creating a qubit type requires passing the mlir context object
        ty = QubitType.get(ctx)
        tensor_shape = tensor.RankedTensorType.get(shape=[1], element_type=ty)
        self.ir = qnet.EprsOp(qout=tensor_shape, N=self.n, remote=self.name)
        return self.ir
