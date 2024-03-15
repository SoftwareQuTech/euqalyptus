from dataclasses import dataclass

from qoala import QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaExpression


@dataclass(init=False)
class GetItem(QoalaOperation):
    base_array: QoalaExpression
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.base_array: QoalaExpression = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class SetItem(QoalaOperation):
    base_array: QoalaExpression
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.base_array: QoalaExpression = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)
