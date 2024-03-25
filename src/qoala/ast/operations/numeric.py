from dataclasses import dataclass

import qnet.dialects.arith as arith
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.errors import WrongEvaluationTypeError
from qoala.ast.operations import QoalaOperation, with_arith_operators
from qoala.ast.value import QoalaInteger, QoalaFloat


@dataclass(init=False)
@with_arith_operators
class Add(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir = arith.addi(self.operand_a.ir, self.operand_b.ir)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir = arith.addf(self.operand_a.ir, self.operand_b.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


@dataclass(init=False)
@with_arith_operators
class Subtract(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir = arith.subi(self.operand_a.ir, self.operand_b.ir)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir = arith.subf(self.operand_a.ir, self.operand_b.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


@dataclass(init=False)
@with_arith_operators
class Multiply(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir = arith.muli(self.operand_a.ir, self.operand_b.ir)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir = arith.mulf(self.operand_a.ir, self.operand_b.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


@dataclass(init=False)
@with_arith_operators
class Divide(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir = arith.divui(self.operand_a.ir, self.operand_b.ir)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir = arith.divf(self.operand_a.ir, self.operand_b.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


class ArithOperatorFactory:
    def __new__(cls, *operands, operation: str) -> QoalaExpression:
        if operation in ["__add__", "__radd__", "__iadd__"]:
            return Add(*operands)
        elif operation in ["__sub__", "__rsub__", "__isub__"]:
            return Subtract(*operands)
        elif operation in ["__mul__", "__rmul__", "__imul__"]:
            return Multiply(*operands)
        elif operation in ["__truediv__", "__rtruediv_", "__itruediv__"]:
            return Divide(*operands)
