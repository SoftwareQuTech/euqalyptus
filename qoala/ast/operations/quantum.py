from dataclasses import dataclass
from enum import Enum, auto

from qoala import QoalaProgram
from qoala.ast import QoalaOperation
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import QoalaExpression, QoalaFloatOrExpression, QoalaIntegerOrExpression


@dataclass(init=False)
class QubitMeasure(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class QubitReset(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class XGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class YGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class ZGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class TGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class HGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class KGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class SGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)


class RotateBaseAxis(Enum):
    X = auto()
    Y = auto()
    Z = auto()


@dataclass(init=False)
class Rotate(QoalaOperation):
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


@dataclass(init=False)
class CNotGate(QoalaOperation):
    target: QoalaQubit

    def __init__(self, target: QoalaExpression):
        assert isinstance(target, QoalaQubit)
        self.target = target
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class CPhaseGate(QoalaOperation):
    target: QoalaQubit

    def __init__(self, target: QoalaExpression):
        assert isinstance(target, QoalaQubit)
        self.target = target
        QoalaProgram.add_to_body(self)
