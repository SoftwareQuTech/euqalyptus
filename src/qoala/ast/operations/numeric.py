from dataclasses import dataclass

from qoala import QoalaProgram
from qoala.ast import QoalaOperation
from qoala.ast.value import QoalaExpression


@dataclass(init=False)
class Add(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class Subtract(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class Multiply(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class Divide(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)
