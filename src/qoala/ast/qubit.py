import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

import qnet.dialects.qnet as qnet
import qnet.dialects.tensor as tensor
from qnet.dialects.qnet import QubitType
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.errors import OperandMismatchError
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.numeric import Pow2, Divide, Multiply
from qoala.ast.value import (
    QoalaInteger,
    QoalaArray,
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


class QbitBaseOperations(QoalaQubit, ABC):
    @staticmethod
    def _process_angles(
            n: ImmediateQIntOrExpression | None = None,
            d: ImmediateQIntOrExpression | None = None,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaExpression:
        # if n and d are immediates, then we can directly compute the value of angle
        if n is not None and d is not None:
            # In this case, we know that n and d are given
            if isinstance(n, int) and isinstance(d, int):
                # angle can be computed at compile time
                angle_result = float(n * math.pi / (math.pow(2, n)))
                angle_val = QoalaNumericValue.from_immediate(angle_result)
            else:
                # n and d are given, but, at least, one of them is not an immediate -> angle is known at runtime
                # moreover, if we encounter an immediate, we need to make it a float for simplicity of the later ops
                if isinstance(n, int):
                    n_val = QoalaNumericValue.from_immediate(float(n))
                else:
                    n_val = n
                if isinstance(d, int):
                    d_val = QoalaNumericValue.from_immediate(float(d))
                else:
                    d_val = d
                # angle_val = (n * \pi) / 2 ** d, this means:
                # $pi = arith.const 3.14 : f32
                pi = QoalaNumericValue.from_immediate(math.pi)
                # $up = arith.mulf $n_f32, $pi : f32
                up = Multiply(n_val, pi)
                # $down = math.exp2 $d : f32 ;; convenient base-2 exponentiation operation
                down = Pow2(d_val)
                # $angle_val = arith.divf $up, $down : f32
                angle_val = Divide(up, down)
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
        angle_val = QbitBaseOperations._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateX
        return QoalaOperation._create_expression_for_op(RotateX, qubit=self, angle=angle_val)

    def rot_Y(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QbitBaseOperations._process_angles(n, d, angle)
        from qoala.ast.operations.quantum import RotateY
        return QoalaOperation._create_expression_for_op(RotateY, qubit=self, angle=angle_val)

    def rot_Z(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QbitBaseOperations._process_angles(n, d, angle)
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


class QoalaLocalQubit(QbitBaseOperations):
    def __init__(self):
        super().__init__()
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        self.ir = qnet.new_qubit()
        return self.ir


@dataclass(init=False)
class QoalaRemoteQubit(QoalaLocalQubit):
    # Is there any difference between a local and an "entangled" local qubit?
    pass


@dataclass(init=False)
class QoalaEprs(QoalaArray[QoalaQubit, int]):
    num_pairs: int
    remote_name: str
    remote: QoalaOperation

    def __init__(self, name: str, n: int):
        self.remote_name = name
        self.num_pairs = n
        # Before using the remote, it needs to be declared
        from qoala.ast.operations.quantum import DeclareRemote
        self.remote = DeclareRemote(self.remote_name)
        super().__init__(base_type=int, base_size=1, length=n)
        # We don't need to add this operation to the body, since it's already done by the
        # call to the constructor on the parent class

    # Special case since EPRS qubits behave like arrays, we need a way to access the entangled qubits
    def __getitem__(self, item_index: ImmediateQIntOrExpression) -> QoalaExpression:
        if isinstance(item_index, int):
            index_operand = QoalaNumericValue.from_immediate(item_index, is_index=True)
        else:
            # The index is already a qoala expression, which can evaluate either to a float or int
            # If it evaluates to an int, we need to cast it to an integer
            if not item_index.can_evaluate_to(QoalaInteger):
                raise OperandMismatchError(f"The index operand '{item_index}' cannot evaluate to an integer, "
                                           f"hence it cannot be used index an array.")
            from qoala.ast.operations.arrays import CastToIndex
            casted_index = QoalaOperation._create_expression_for_op(CastToIndex, item_index)
            index_operand = casted_index
        from qoala.ast.operations.arrays import GetQItem
        return QoalaOperation._create_expression_for_op(GetQItem, self, index_operand)

    # Functions for generating IR
    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaQubit

    def to_ir(self, ctx: Context):
        # Creating a qubit type requires passing the mlir context object
        ty = QubitType.get(ctx)
        tensor_shape = tensor.RankedTensorType.get(shape=[self.num_pairs], element_type=ty)
        self.ir = qnet.EprsOp(qout=tensor_shape, N=self.num_pairs, remote=self.remote_name)
        return self.ir

