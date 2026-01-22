from abc import ABC
from dataclasses import dataclass
from typing import Optional

import qnet.dialects.arith as arith
import qnet.dialects.math as math
from qnet.ir import Context, Location

from qoala.ast import QoalaExpression, checkbaseir
from qoala.ast.operations import (
    QoalaOperation,
    with_arith_operators,
    with_order_operators,
)
from qoala.ast.operations.casts import IntToFloat
from qoala.ast.value import QoalaInteger, QoalaFloat
from qoala.errors import WrongEvaluationTypeError, UnknownOperationError
from qoala.utils.debug_info import get_debug_info


@dataclass(init=False)
class BaseBinaryArithOp(QoalaOperation, ABC):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        # We "normalize" the operands, upcasting an integer to a float if needed
        assert len(operands) == 2
        if not (
            operands[0].can_evaluate_to(QoalaFloat)
            or operands[0].can_evaluate_to(QoalaInteger)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[0]}' cannot evaluate to "
                f"either Integer or Float"
            )
        elif not (
            operands[1].can_evaluate_to(QoalaFloat)
            or operands[1].can_evaluate_to(QoalaInteger)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[1]}' cannot evaluate to "
                f"either Integer or Float"
            )
        elif operands[0].can_evaluate_to(QoalaFloat) and operands[1].can_evaluate_to(
            QoalaInteger
        ):
            # We need to add a cast of operand[1]
            casted_operand_1 = IntToFloat(operands[1])
            self.operand_a = operands[0]
            self.operand_b = casted_operand_1
        elif operands[1].can_evaluate_to(QoalaFloat) and operands[0].can_evaluate_to(
            QoalaInteger
        ):
            # We need to add a cast of operand a
            casted_operand_0 = IntToFloat(operands[0])
            self.operand_a = casted_operand_0
            self.operand_b = operands[1]
        else:
            self.operand_a = operands[0]
            self.operand_b = operands[1]


@dataclass(init=False)
@with_order_operators
@with_arith_operators
class Add(BaseBinaryArithOp):

    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return (
            (cls == QoalaInteger or cls == QoalaFloat)
            and self.operand_a.can_evaluate_to(cls)
            and self.operand_b.can_evaluate_to(cls)
        )

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir_value = arith.addi(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir_value = arith.addf(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@dataclass(init=False)
@with_order_operators
@with_arith_operators
class Subtract(BaseBinaryArithOp):

    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return (
            (cls == QoalaInteger or cls == QoalaFloat)
            and self.operand_a.can_evaluate_to(cls)
            and self.operand_b.can_evaluate_to(cls)
        )

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir_value = arith.subi(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir_value = arith.subf(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@dataclass(init=False)
@with_order_operators
@with_arith_operators
class Multiply(BaseBinaryArithOp):

    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return (
            (cls == QoalaInteger or cls == QoalaFloat)
            and self.operand_a.can_evaluate_to(cls)
            and self.operand_b.can_evaluate_to(cls)
        )

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir_value = arith.muli(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir_value = arith.mulf(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@dataclass(init=False)
@with_order_operators
@with_arith_operators
class Divide(BaseBinaryArithOp):
    """
    Represents a "divide" operation, which accepts 2 operands.
    This divide operation can accept operands that can *both* evaluate to either
    ``QoalaInteger`` or ``QoalaFloat``. The result of this operation (what does this
    operation can evaluate to) is of the same type of *both* of the given operands.
    """

    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        return (
            (cls == QoalaInteger or cls == QoalaFloat)
            and self.operand_a.can_evaluate_to(cls)
            and self.operand_b.can_evaluate_to(cls)
        )

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir_value = arith.divui(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir_value = arith.divf(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@dataclass(init=False)
@with_order_operators
@with_arith_operators
class Pow(QoalaOperation):
    base: QoalaExpression
    exponent: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        self.base = operands[0]
        self.exponent = operands[1]
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return (cls == QoalaInteger or cls == QoalaFloat) and self.base.can_evaluate_to(
            cls
        )  # The base of the exponentiation dictates the type of the result

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.base.can_evaluate_to(QoalaInteger) and self.exponent.can_evaluate_to(
            QoalaInteger
        ):
            # Both base and exponents can evaluate to integers
            self.ir_value = math.powf(
                self.base.ir_value, self.exponent.ir_value, loc=source_location
            )
        elif self.base.can_evaluate_to(QoalaFloat) and self.exponent.can_evaluate_to(
            QoalaFloat
        ):
            # Both base and exponents can evaluate to floats
            self.ir_value = math.ipowi(
                self.base.ir_value, self.exponent.ir_value, loc=source_location
            )
        elif self.base.can_evaluate_to(QoalaFloat) and self.exponent.can_evaluate_to(
            QoalaInteger
        ):
            # Both base and exponents can evaluate to floats
            self.ir_value = math.fpowi(
                self.base.ir_value, self.exponent.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@dataclass(init=False)
@with_order_operators
@with_arith_operators
class Pow2(QoalaOperation):
    exponent: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        if operands[0].can_evaluate_to(QoalaInteger):
            # The operand must be casted to float
            self.exponent = IntToFloat(operands[0])
        else:
            self.exponent = operands[0]
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaFloat

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.exponent.can_evaluate_to(QoalaInteger) or self.exponent.can_evaluate_to(
            QoalaFloat
        ):
            self.ir_value = math.exp2(self.exponent.ir_value, loc=source_location)
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


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
        else:
            raise UnknownOperationError(f"Operation '{operation}' is not supported")
