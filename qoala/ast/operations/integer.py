from qoala.ast import QoalaOperation
from qoala.ast.value import QoalaInteger


class Add(QoalaOperation):

    operand_a: QoalaInteger
    operand_b: QoalaInteger

    def __init__(self, operand_a: QoalaInteger, operand_b: QoalaInteger):
        self.operand_a = operand_a
        self.operand_b = operand_b

    def get_value(self) -> QoalaInteger:
        pass

