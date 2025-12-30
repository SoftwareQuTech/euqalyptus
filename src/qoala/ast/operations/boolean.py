from abc import ABC
from dataclasses import dataclass
from typing import Optional

from qnet.dialects import arith
from qnet.extras.types import bool as mlir_bool
from qnet.ir import Context, Location

from qoala import QoalaProgram
from qoala.ast import QoalaExpression, checkbaseir
from qoala.ast.operations import QoalaOperation, with_bool_operators
from qoala.ast.value import QoalaBool
from qoala.errors import UnknownOperationError, WrongEvaluationTypeError


@dataclass(init=False)
class BaseUnaryBoolOp(QoalaOperation, ABC):
    operand: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        # We "normalize" the operands, upcasting an integer to a float if needed
        assert len(operands) == 1
        if not (
            operands[0].can_evaluate_to(QoalaBool)
            or operands[0].can_evaluate_to(QoalaBool)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[0]}' cannot evaluate to "
                f"either Integer or Float"
            )
        # TODO - Allow integers to be casted to bools? (0 -> False, !=0 -> True)?
        self.operand = operands[0]


@dataclass(init=False)
class BaseBinaryBoolOp(QoalaOperation, ABC):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        # We "normalize" the operands, upcasting an integer to a float if needed
        assert len(operands) == 2
        if not (
            operands[0].can_evaluate_to(QoalaBool)
            or operands[0].can_evaluate_to(QoalaBool)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[0]}' cannot evaluate to "
                f"either Integer or Float"
            )
        elif not (
            operands[1].can_evaluate_to(QoalaBool)
            or operands[1].can_evaluate_to(QoalaBool)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[1]}' cannot evaluate to "
                f"either Integer or Float"
            )
        # TODO - Allow integers to be casted to bools? (0 -> False, !=0 -> True)?
        self.operand_a = operands[0]
        self.operand_b = operands[1]


@with_bool_operators
class And(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaBool):
            self.ir_value = arith.andi(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@with_bool_operators
class Or(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaBool):
            self.ir_value = arith.ori(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@with_bool_operators
class Xor(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaBool):
            self.ir_value = arith.xori(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@with_bool_operators
class Not(BaseUnaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # There is no "bitwise negate" operation in arith, but we can xor with 0xFF
        if self.operand.can_evaluate_to(QoalaBool):
            bool_type = mlir_bool()
            source_location = Location.file(
                filename=self.debug_info.filename,
                line=self.debug_info.line_start,
                col=self.debug_info.col_start,
                context=ctx,
            )
            true_op = arith.constant(value=True, result=bool_type, loc=source_location)
            self.ir_value = true_op
            self.ir_value = arith.xori(
                self.operand.ir_value, true_op, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


class BooleanOperatorFactory:
    def __new__(cls, *operands, operation: str) -> QoalaExpression:
        if operation in ["__and__", "__rand__"]:
            return And(*operands)
        elif operation in ["__or__", "__ror__"]:
            return Or(*operands)
        elif operation in ["__xor__", "__rxor__"]:
            return Xor(*operands)
        elif operation in ["__neg__", "__invert__"]:
            return Not(*operands)
        else:
            raise UnknownOperationError(f"Operation '{operation}' is not supported")
