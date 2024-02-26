from dataclasses import dataclass

from qoala import QoalaProgram
from qoala.ast import QoalaOperation, FloatOrExpression, IntegerOrExpression
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import QoalaExpression


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


@dataclass(init=False)
class RotateX(QoalaOperation):
    n: IntegerOrExpression
    d: IntegerOrExpression
    angle: FloatOrExpression

    def __init__(self, *operands: QoalaExpression):
        # TODO - Implement the transformation of immediates to expressions
        pass


@dataclass(init=False)
class RotateY(QoalaOperation):
    n: IntegerOrExpression
    d: IntegerOrExpression
    angle: FloatOrExpression

    def __init__(self, *operands: QoalaExpression):
        # TODO - Implement the transformation of immediates to expressions
        pass


@dataclass(init=False)
class RotateZ(QoalaOperation):
    n: IntegerOrExpression
    d: IntegerOrExpression
    angle: FloatOrExpression

    def __init__(self, *operands: QoalaExpression):
        # TODO - Implement the transformation of immediates to expressions
        pass
