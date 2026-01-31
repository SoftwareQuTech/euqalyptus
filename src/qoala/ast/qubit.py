import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

import qnet.dialects.qnet as qnet
from qnet.ir import Context, Location
from typing_extensions import Self

from qoala.ast import QoalaExpression, checkbaseir
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.casts import FloatToInt
from qoala.ast.operations.numeric import Pow2, Divide, Multiply
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaNumericValue
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
        n: QoalaInteger | QoalaExpression | int = 0,
        d: QoalaInteger | QoalaExpression | int = 0,
        angle: QoalaFloat | QoalaExpression | float | None = None,
    ) -> QoalaOperation:
        pass

    @abstractmethod
    def rot_Y(
        self,
        n: QoalaInteger | QoalaExpression | int = 0,
        d: QoalaInteger | QoalaExpression | int = 0,
        angle: QoalaFloat | QoalaExpression | float | None = None,
    ) -> QoalaOperation:
        pass

    @abstractmethod
    def rot_Z(
        self,
        n: QoalaInteger | QoalaExpression | int = 0,
        d: QoalaInteger | QoalaExpression | int = 0,
        angle: QoalaFloat | QoalaExpression | float | None = None,
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


class QubitBaseOperations(QoalaQubit, ABC):

    @staticmethod
    def _process_angles(
        n: QoalaInteger | QoalaExpression | int | None = None,
        d: QoalaInteger | QoalaExpression | int | None = None,
        angle: QoalaFloat | QoalaExpression | float | None = None,
        dbg_info: DebugInfo | None = None,
    ) -> Tuple[QoalaExpression, Optional[QoalaExpression]]:
        if dbg_info is None:
            raise RuntimeError("Unknown debug info")
        angle_val_a: QoalaExpression
        angle_val_b: Optional[QoalaExpression]
        # First, we check if the angle was given
        if angle is not None:
            if isinstance(angle, float):
                # Angle was given as an immediate
                angle_val_a = QoalaNumericValue.from_immediate(angle, dbg_info)
                angle_val_b = None
            elif isinstance(angle, (QoalaFloat, QoalaExpression, float)):
                # Angle can be evaluated at runtime
                angle_val_a = angle
                angle_val_b = None
        # if n and d are immediates, then we can create integer-based rotations
        elif n is not None and d is not None:
            # In this case, we know that n and d are given
            if isinstance(n, int) and isinstance(d, int):
                angle_val_a = QoalaNumericValue.from_immediate(n, dbg_info)
                angle_val_b = QoalaNumericValue.from_immediate(d, dbg_info)
            else:
                # n and d are given, but, at least, one of them is not an immediate
                if isinstance(n, int):
                    angle_val_a = QoalaNumericValue.from_immediate(n, dbg_info)
                else:
                    if n.can_evaluate_to(QoalaFloat):
                        angle_val_a = FloatToInt(n)
                    else:
                        # Here we assume that "n" is a runtime value, and it can evaluate to QoalaInt
                        assert n.can_evaluate_to(QoalaInteger)
                        angle_val_a = n
                if isinstance(d, int):
                    angle_val_b = QoalaNumericValue.from_immediate(d, dbg_info)
                else:
                    if d.can_evaluate_to(QoalaFloat):
                        angle_val_b = FloatToInt(d)
                    else:
                        # Here we assume that "n" is a runtime value, and it can evaluate to QoalaInt
                        assert d.can_evaluate_to(QoalaInteger)
                        angle_val_b = d
                # # angle_val = (n * \pi) / 2 ** d, this means:
                # # $pi = arith.const 3.14 : f32
                # pi = QoalaNumericValue.from_immediate(math.pi, dbg_info)
                # # $up = arith.mulf $n_f32, $pi : f32
                # up = Multiply(n_val, pi)
                # # $down = math.exp2 $d : f32 ;; convenient base-2 exponentiation operation
                # down = Pow2(d_val)
                # # $angle_val = arith.divf $up, $down : f32
                # angle_val_a = Divide(up, down)
        else:
            # Worst-worst case... we have nothing
            angle_val_a = QoalaNumericValue.from_immediate(0.0, dbg_info)
            angle_val_b = None
        return angle_val_a, angle_val_b

    def measure(self) -> QoalaOperation:
        # When we measure, _at runtime_ we get a value of type Bit (or QoalaBit).
        # However, here we need to model how the measure operation is compiled
        # Being this said, we need to return a "QubitMeasure" operation
        from qoala.ast.operations.quantum import QubitMeasure

        # TODO - Do we need to specify the base?
        return QubitMeasure(self)

    def X(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import XGate

        return QoalaOperation.create_expression_for_op(XGate, self)

    def Y(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import YGate

        return QoalaOperation.create_expression_for_op(YGate, self)

    def Z(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import ZGate

        return QoalaOperation.create_expression_for_op(ZGate, self)

    def T(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import TGate

        return QoalaOperation.create_expression_for_op(TGate, self)  # type: ignore[type-abstract]

    def H(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import HGate

        return QoalaOperation.create_expression_for_op(HGate, self)

    def S(self) -> QoalaOperation:
        from qoala.ast.operations.quantum import SGate

        return QoalaOperation.create_expression_for_op(SGate, self)  # type: ignore[type-abstract]

    def rot_X(
        self,
        n: QoalaInteger | QoalaExpression | int = 0,
        d: QoalaInteger | QoalaExpression | int = 0,
        angle: QoalaFloat | QoalaExpression | float | None = None,
    ) -> QoalaOperation:
        angle_val_a, angle_val_b = QubitBaseOperations._process_angles(
            n, d, angle, self.debug_info
        )
        from qoala.ast.operations.quantum import RotateX

        if angle_val_a.can_evaluate_to(QoalaFloat):
            return QoalaOperation.create_expression_for_op(
                RotateX, qubit=self, angle=angle_val_a
            )
        else:
            # Here we assume that n and d are given, and they can evaluate to QoalaInteger
            assert angle_val_a.can_evaluate_to(QoalaInteger)
            assert angle_val_b is not None and angle_val_b.can_evaluate_to(QoalaInteger)
            return QoalaOperation.create_expression_for_op(
                RotateX, qubit=self, n=angle_val_a, d=angle_val_b
            )

    def rot_Y(
        self,
        n: QoalaInteger | QoalaExpression | int = 0,
        d: QoalaInteger | QoalaExpression | int = 0,
        angle: QoalaFloat | QoalaExpression | float | None = None,
    ) -> QoalaOperation:
        angle_val_a, angle_val_b = QubitBaseOperations._process_angles(
            n, d, angle, self.debug_info
        )
        from qoala.ast.operations.quantum import RotateY

        if angle_val_a.can_evaluate_to(QoalaFloat):
            return QoalaOperation.create_expression_for_op(
                RotateY, qubit=self, angle=angle_val_a
            )
        else:
            # Here we assume that n and d are given, and they can evaluate to QoalaInteger
            assert angle_val_a.can_evaluate_to(QoalaInteger)
            assert angle_val_b is not None and angle_val_b.can_evaluate_to(QoalaInteger)
            return QoalaOperation.create_expression_for_op(
                RotateY, qubit=self, n=angle_val_a, d=angle_val_b
            )

    def rot_Z(
        self,
        n: QoalaInteger | QoalaExpression | int = 0,
        d: QoalaInteger | QoalaExpression | int = 0,
        angle: QoalaFloat | QoalaExpression | float | None = None,
    ) -> QoalaOperation:
        angle_val_a, angle_val_b = QubitBaseOperations._process_angles(
            n, d, angle, self.debug_info
        )
        from qoala.ast.operations.quantum import RotateZ

        if angle_val_a.can_evaluate_to(QoalaFloat):
            return QoalaOperation.create_expression_for_op(
                RotateZ, qubit=self, angle=angle_val_a
            )
        else:
            # Here we assume that n and d are given, and they can evaluate to QoalaInteger
            assert angle_val_a.can_evaluate_to(QoalaInteger)
            assert angle_val_b is not None and angle_val_b.can_evaluate_to(QoalaInteger)
            return QoalaOperation.create_expression_for_op(
                RotateZ, qubit=self, n=angle_val_a, d=angle_val_b
            )

    def cnot(self, target: Self) -> QoalaOperation:
        from qoala.ast.operations.quantum import CNotGate

        return QoalaOperation.create_expression_for_op(
            CNotGate, qubit=self, target=target
        )

    def cphase(self, target: Self) -> QoalaOperation:
        from qoala.ast.operations.quantum import CPhaseGate

        return QoalaOperation.create_expression_for_op(
            CPhaseGate, qubit=self, target=target
        )

    def cz(self, target: Self) -> QoalaOperation:
        return self.cphase(target)

    def free(self) -> QoalaOperation:  # type: ignore[empty-body]
        # TODO - Implement
        pass


class QoalaLocalQubit(QubitBaseOperations):

    def __init__(self):
        super().__init__()
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaQubit

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = qnet.new_qubit(loc=source_location)


# This class represents a "remote" qubit, i.e. an entangled qubit
# It behaves like a single qubit, so you can perform any "traditional"
# operations on this qubit
@dataclass(init=False)
class QoalaEprs(QubitBaseOperations):
    remote_name: str

    def __init__(self, name: str):
        super().__init__()
        # We assume the remote was declared before using the name (symbol)
        self.remote_name = name
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaQubit

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = qnet.eprs(remote=self.remote_name, loc=source_location)
