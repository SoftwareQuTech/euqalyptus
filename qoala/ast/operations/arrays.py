from qoala.ast import QoalaOperation
from qoala.ast.value import QoalaExpression


class GetItem(QoalaOperation):
    base_array: QoalaExpression
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.base_array = operands[0]
        self.index = operands[1]
