from abc import ABC
from dataclasses import dataclass

import qnet.dialects.arith as arith
import qnet.dialects.math as math
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.errors import WrongEvaluationTypeError
from qoala.ast.operations import with_arith_operators
from qoala.ast.operations.casts import IntToFloat
from qoala.ast.value import QoalaInteger, QoalaFloat


@dataclass(init=False)
class BaseBinaryArithOp(QoalaExpression, ABC):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        # We "normalize" the operands, upcasting an integer to a float if needed
        assert len(operands) == 2
        if not (operands[0].can_evaluate_to(QoalaFloat) or operands[0].can_evaluate_to(QoalaInteger)):
            raise WrongEvaluationTypeError(f"When constructing operation '{self.__class__.__name__}': "
                                           f"One of the operands '{operands[0]}' cannot evaluate to "
                                           f"either Integer or Float")
        elif not (operands[1].can_evaluate_to(QoalaFloat) or operands[1].can_evaluate_to(QoalaInteger)):
            raise WrongEvaluationTypeError(f"When constructing operation '{self.__class__.__name__}': "
                                           f"One of the operands '{operands[1]}' cannot evaluate to "
                                           f"either Integer or Float")
        elif operands[0].can_evaluate_to(QoalaFloat) and operands[1].can_evaluate_to(QoalaInteger):
            # We need to add a cast of operand[1]
            casted_operand_1 = IntToFloat(operands[1])
            self.operand_a = operands[0]
            self.operand_b = casted_operand_1
        elif operands[1].can_evaluate_to(QoalaFloat) and operands[0].can_evaluate_to(QoalaInteger):
            # We need to add a cast of operand a
            casted_operand_0 = IntToFloat(operands[0])
            self.operand_a = casted_operand_0
            self.operand_b = operands[1]
        else:
            self.operand_a = operands[0]
            self.operand_b = operands[1]


@with_arith_operators
class Add(BaseBinaryArithOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return ((cls == QoalaInteger or cls == QoalaFloat) and
                self.operand_a.can_evaluate_to(cls) and
                self.operand_b.can_evaluate_to(cls))

    def to_ir(self, ctx: Context):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir = arith.addi(self.operand_a.ir, self.operand_b.ir)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir = arith.addf(self.operand_a.ir, self.operand_b.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


@with_arith_operators
class Subtract(BaseBinaryArithOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return ((cls == QoalaInteger or cls == QoalaFloat) and
                self.operand_a.can_evaluate_to(cls) and
                self.operand_b.can_evaluate_to(cls))

    def to_ir(self, ctx: Context):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
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
class Multiply(BaseBinaryArithOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return ((cls == QoalaInteger or cls == QoalaFloat) and
                self.operand_a.can_evaluate_to(cls) and
                self.operand_b.can_evaluate_to(cls))

    def to_ir(self, ctx: Context):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
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
class Divide(BaseBinaryArithOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return ((cls == QoalaInteger or cls == QoalaFloat) and
                self.operand_a.can_evaluate_to(cls) and
                self.operand_b.can_evaluate_to(cls))

    def to_ir(self, ctx: Context):
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir = arith.divui(self.operand_a.ir, self.operand_b.ir)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir = arith.divf(self.operand_a.ir, self.operand_b.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


@dataclass(init=False)
@with_arith_operators
class Pow(QoalaExpression):
    base: QoalaExpression
    exponent: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        self.base = operands[0]
        self.exponent = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        return ((cls == QoalaInteger or cls == QoalaFloat) and
                self.base.can_evaluate_to(cls))  # The base of the exponentiation dictates the type of the result

    def to_ir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.base.can_evaluate_to(QoalaInteger) and self.exponent.can_evaluate_to(QoalaInteger):
            # Both base and exponents can evaluate to integers
            self.ir = math.powf(self.base.ir, self.exponent.ir)
        elif self.base.can_evaluate_to(QoalaFloat) and self.exponent.can_evaluate_to(QoalaFloat):
            # Both base and exponents can evaluate to floats
            self.ir = math.ipowi(self.base.ir, self.exponent.ir)
        elif self.base.can_evaluate_to(QoalaFloat) and self.exponent.can_evaluate_to(QoalaInteger):
            # Both base and exponents can evaluate to floats
            self.ir = math.fpowi(self.base.ir, self.exponent.ir)
        else:
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self.ir


@dataclass(init=False)
@with_arith_operators
class Pow2(QoalaExpression):
    exponent: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        if operands[0].can_evaluate_to(QoalaInteger):
            # The operand must be casted to float
            self.exponent = IntToFloat(operands[0])
        else:
            self.exponent = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        return cls == QoalaFloat

    def to_ir(self, ctx: Context):
        if self.exponent.can_evaluate_to(QoalaInteger) or self.exponent.can_evaluate_to(QoalaFloat):
            self.ir = math.exp2(self.exponent.ir)
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
