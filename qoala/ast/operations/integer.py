from qoala.ast import QoalaOperation
from qoala.ast.value import QoalaInteger, QoalaExpression


class Add(QoalaOperation):

    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, operand_a: QoalaExpression, operand_b: QoalaExpression):
        self.operand_a = operand_a
        self.operand_b = operand_b

    def get_value(self) -> QoalaInteger:
        pass

