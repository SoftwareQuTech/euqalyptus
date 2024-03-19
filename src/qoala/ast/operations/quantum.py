from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

from qoala import QoalaProgram
from qoala.ast.errors import OperationNotYetImplementedError
from qoala.ast.operations import QoalaOperation
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import QoalaExpression, QoalaFloatOrExpression, QoalaIntegerOrExpression, QoalaBit

from qoalahir.ir import Context
import qoalahir.dialects.hir as hir


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
        self._qoala_hir_val = hir.measure(qin0=self.qubit._qoala_hir_val)
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
        raise OperationNotYetImplementedError(QubitReset.__name__)


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
        raise OperationNotYetImplementedError(XGate.__name__)


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
        raise OperationNotYetImplementedError(YGate.__name__)


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
        raise OperationNotYetImplementedError(ZGate.__name__)


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
        raise OperationNotYetImplementedError(TGate.__name__)


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
        self._qoala_hir_val = hir.hadamard(self.qubit)
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
        raise OperationNotYetImplementedError(KGate.__name__)


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
        raise OperationNotYetImplementedError(SGate.__name__)


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
        self._qoala_hir_val = hir.rot_x(qin=self.qubit._qoala_hir_val, angle=self.angle._qoala_hir_val)
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
        self._qoala_hir_val = hir.rot_y(qin=self.qubit._qoala_hir_val, angle=self.angle._qoala_hir_val)
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
        self._qoala_hir_val = hir.rot_z(qin=self.qubit._qoala_hir_val, angle=self.angle._qoala_hir_val)
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
        self._qoala_hir_val = hir.cnot(qin0=self.qubit._qoala_hir_val, qin1=self.target._qoala_hir_val)
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
        raise OperationNotYetImplementedError(CPhaseGate.__name__)
