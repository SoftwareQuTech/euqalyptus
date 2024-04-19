import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

import qnet.dialects.qnet as qnet
from qnet.ir import Context, Location

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.numeric import Pow2, Divide, Multiply
from qoala.ast.value import (
    QoalaNumericValue,
    ImmediateQIntOrExpression,
    ImmediateQFloatOrExpression,
    QoalaFloatOrExpression
)
from qoala.utils.debug_info import DebugInfo, get_debug_info


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
    def cz(self, target: Self) -> QoalaOperation:
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
            angle: ImmediateQFloatOrExpression | None = None,
            dbg_info: DebugInfo | None = None,
    ) -> QoalaExpression:
        if dbg_info is None:
            raise RuntimeError(f"Unknown debug info")
        # First, we check if the angle was given
        if angle is not None:
            if isinstance(angle, float):
                # Angle was given as an immediate
                angle_val = QoalaNumericValue.from_immediate(angle, dbg_info)
            elif isinstance(angle, QoalaFloatOrExpression):
                # Angle can be evaluated at runtime
                angle_val = angle
        # if n and d are immediates, then we can directly compute the value of angle
        elif n is not None and d is not None:
            # In this case, we know that n and d are given
            if isinstance(n, int) and isinstance(d, int):
                # angle can be computed at compile time
                angle_result = float(n * math.pi / (math.pow(2, n)))
                angle_val = QoalaNumericValue.from_immediate(angle_result, dbg_info)
            else:
                # n and d are given, but, at least, one of them is not an immediate -> angle is known at runtime
                # moreover, if we encounter an immediate, we need to make it a float for simplicity of the later ops
                if isinstance(n, int):
                    n_val = QoalaNumericValue.from_immediate(float(n), dbg_info)
                else:
                    n_val = n
                if isinstance(d, int):
                    d_val = QoalaNumericValue.from_immediate(float(d), dbg_info)
                else:
                    d_val = d
                # angle_val = (n * \pi) / 2 ** d, this means:
                # $pi = arith.const 3.14 : f32
                pi = QoalaNumericValue.from_immediate(math.pi, dbg_info)
                # $up = arith.mulf $n_f32, $pi : f32
                up = Multiply(n_val, pi)
                # $down = math.exp2 $d : f32 ;; convenient base-2 exponentiation operation
                down = Pow2(d_val)
                # $angle_val = arith.divf $up, $down : f32
                angle_val = Divide(up, down)
        else:
            # Worst-worst case... we have nothing
            angle_val = QoalaNumericValue.from_immediate(0.0, dbg_info)
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

    def S(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import SGate
        return QoalaOperation._create_expression_for_op(SGate, self)

    def rot_X(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QbitBaseOperations._process_angles(n, d, angle, self.debug_info)
        from qoala.ast.operations.quantum import RotateX
        return QoalaOperation._create_expression_for_op(RotateX, qubit=self, angle=angle_val)

    def rot_Y(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QbitBaseOperations._process_angles(n, d, angle, self.debug_info)
        from qoala.ast.operations.quantum import RotateY
        return QoalaOperation._create_expression_for_op(RotateY, qubit=self, angle=angle_val)

    def rot_Z(
            self,
            n: ImmediateQIntOrExpression = 0,
            d: ImmediateQIntOrExpression = 0,
            angle: ImmediateQFloatOrExpression | None = None
    ) -> QoalaOperation:
        angle_val = QbitBaseOperations._process_angles(n, d, angle, self.debug_info)
        from qoala.ast.operations.quantum import RotateZ
        return QoalaOperation._create_expression_for_op(RotateZ, qubit=self, angle=angle_val)

    def cnot(self, target: Self) -> QoalaOperation:
        from qoala.ast.operations.quantum import CNotGate
        return QoalaOperation._create_expression_for_op(CNotGate, qubit=self, target=target)

    def cphase(self, target: Self) -> QoalaOperation:
        from qoala.ast.operations.quantum import CPhaseGate
        return QoalaOperation._create_expression_for_op(CPhaseGate, qubit=self, target=target)

    def cz(self, target: Self) -> QoalaOperation:
        return self.cphase(target)

    def free(self) -> QoalaOperation:
        # TODO - Implement
        pass


class QoalaLocalQubit(QbitBaseOperations):
    def __init__(self):
        super().__init__()
        self.debug_info = get_debug_info()
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        return cls == QoalaQubit

    def to_ir(self, ctx: Context):
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx
        )
        self.ir = qnet.new_qubit(loc=source_location)
        return self.ir


# This class represents a "remote" qubit, i.e. an entangled qubit
# It behaves like a single qubit, so you can perform any "traditional"
# operations on this qubit
@dataclass(init=False)
class QoalaEprs(QbitBaseOperations):
    remote_name: str

    def __init__(self, name: str):
        super().__init__()
        # We assume the remote was declared before using the name (symbol)
        self.remote_name = name
        self.debug_info = get_debug_info()
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        return cls == QoalaQubit

    def to_ir(self, ctx: Context):
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx
        )
        self.ir = qnet.eprs(remote=self.remote_name, loc=source_location)
        return self.ir
