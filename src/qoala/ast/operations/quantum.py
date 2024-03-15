from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

from qoala import QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import QoalaExpression, QoalaFloatOrExpression, QoalaIntegerOrExpression, QoalaBit

from qoalahir.ir import Context
from qoalahir.dialects.hir import HadamardOp, RotXOp, RotYOp, RotZOp, CnotOp, MeasureOp


@dataclass(init=False)
class QubitMeasure(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaBit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self._qoala_hir_val = MeasureOp(qin0=self.qubit)
        return self._qoala_hir_val


@dataclass(init=False)
class QubitReset(QoalaOperation, ABC):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        # "void" operation; can always evaluate to anything
        return True

    def to_hir(self, ctx: Context):
        # TODO - There is no "ResetOp" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class XGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "XGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class YGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "YGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class ZGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "ZGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class TGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "TGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class HGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self._qoala_hir_val = HadamardOp(self.qubit)
        return self._qoala_hir_val


@dataclass(init=False)
class KGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "KGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class SGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "SGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val


class RotateBaseAxis(Enum):
    X = auto()
    Y = auto()
    Z = auto()


@dataclass(init=False)
class Rotate(QoalaOperation, ABC):
    qubit: QoalaQubit
    n: QoalaIntegerOrExpression
    d: QoalaIntegerOrExpression
    angle: QoalaFloatOrExpression

    def __init__(
            self,
            qubit: QoalaExpression,
            n: QoalaIntegerOrExpression,
            d: QoalaIntegerOrExpression,
            angle: QoalaFloatOrExpression,
            axis: RotateBaseAxis
    ):
        # We assume the users of this class will pass _at least_ default values for all operands
        assert isinstance(qubit, QoalaQubit)
        self.qubit = qubit
        self.n = n
        self.d = d
        self.angle = angle
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class RotateX(Rotate):
    def __init__(
            self,
            qubit: QoalaExpression,
            n: QoalaIntegerOrExpression,
            d: QoalaIntegerOrExpression,
            angle: QoalaFloatOrExpression
    ):
        super().__init__(qubit=qubit, n=n, d=d, angle=angle, axis=RotateBaseAxis.X)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self._qoala_hir_val = RotXOp(qin=self.qubit, angle=self.angle)
        return self._qoala_hir_val


@dataclass(init=False)
class RotateY(Rotate):
    def __init__(
            self,
            qubit: QoalaExpression,
            n: QoalaIntegerOrExpression,
            d: QoalaIntegerOrExpression,
            angle: QoalaFloatOrExpression
    ):
        super().__init__(qubit=qubit, n=n, d=d, angle=angle, axis=RotateBaseAxis.Y)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self._qoala_hir_val = RotYOp(qin=self.qubit, angle=self.angle)
        return self._qoala_hir_val



@dataclass(init=False)
class RotateZ(Rotate):
    def __init__(
            self,
            qubit: QoalaExpression,
            n: QoalaIntegerOrExpression,
            d: QoalaIntegerOrExpression,
            angle: QoalaFloatOrExpression
    ):
        super().__init__(qubit=qubit, n=n, d=d, angle=angle, axis=RotateBaseAxis.Z)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self._qoala_hir_val = RotZOp(qin=self.qubit, angle=self.angle)
        return self._qoala_hir_val



@dataclass(init=False)
class CNotGate(QoalaOperation):
    quibit: QoalaQubit
    target: QoalaQubit

    def __init__(self, qubit: QoalaExpression, target: QoalaExpression):
        assert isinstance(qubit, QoalaQubit)
        assert isinstance(target, QoalaQubit)
        self.target = target
        self.qubit = qubit
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self._qoala_hir_val = CnotOp(qin0=self.qubit, quin1=self.target)
        return self._qoala_hir_val


@dataclass(init=False)
class CPhaseGate(QoalaOperation):
    target: QoalaQubit

    def __init__(self, target: QoalaExpression):
        assert isinstance(target, QoalaQubit)
        self.target = target
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - There is no "CPhaseGate" operation in hir dialect
        self._qoala_hir_val = None
        return self._qoala_hir_val
