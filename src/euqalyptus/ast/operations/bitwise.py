from abc import ABC
from dataclasses import dataclass
from typing import Optional

from qnet.dialects import arith
from qnet.extras.types import i32, bool as mlir_bool
from qnet.ir import Context, Location

from euqalyptus.ast import QoalaExpression, checkbaseir
from euqalyptus.ast.operations import QoalaOperation, with_operators
from euqalyptus.ast.value import QoalaBool, QoalaInteger
from euqalyptus.errors import UnknownOperationError, WrongEvaluationTypeError


@dataclass(init=False)
class BaseUnaryBitwiseOp(QoalaOperation, ABC):
    operand: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        # We "normalize" the operands, upcasting an integer to a float if needed
        assert len(operands) == 1
        if not (
            operands[0].can_evaluate_to(QoalaBool)
            or operands[0].can_evaluate_to(QoalaInteger)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[0]}' cannot evaluate to "
                f"either Integer or Float"
            )
        # TODO - Allow integers to be casted to bools? (0 -> False, !=0 -> True)?
        self.operand = operands[0]


@dataclass(init=False)
class BaseBinaryBitwiseOp(QoalaOperation, ABC):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        # We "normalize" the operands, upcasting an integer to a float if needed
        assert len(operands) == 2
        if not (
            operands[0].can_evaluate_to(QoalaBool)
            or operands[0].can_evaluate_to(QoalaInteger)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[0]}' cannot evaluate to "
                f"either Integer or Float"
            )
        elif not (
            operands[1].can_evaluate_to(QoalaBool)
            or operands[1].can_evaluate_to(QoalaInteger)
        ):
            raise WrongEvaluationTypeError(
                f"When constructing operation '{self.__class__.__name__}': "
                f"One of the operands '{operands[1]}' cannot evaluate to "
                f"either Integer or Float"
            )
        # TODO - Allow integers to be casted to bools? (0 -> False, !=0 -> True)?
        self.operand_a = operands[0]
        self.operand_b = operands[1]


@with_operators(arith=False, bitwise=True, order=False)
class AndOp(BaseBinaryBitwiseOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from euqalyptus import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaBool or cls is QoalaInteger

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaBool) or self.operand_a.can_evaluate_to(
            QoalaInteger
        ):
            self.ir_value = arith.andi(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@with_operators(arith=False, bitwise=True, order=False)
class OrOp(BaseBinaryBitwiseOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from euqalyptus import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaBool or cls is QoalaInteger

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaBool) or self.operand_a.can_evaluate_to(
            QoalaInteger
        ):
            self.ir_value = arith.ori(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@with_operators(arith=False, bitwise=True, order=False)
class XorOp(BaseBinaryBitwiseOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from euqalyptus import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaBool or cls is QoalaInteger

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaBool) or self.operand_a.can_evaluate_to(
            QoalaInteger
        ):
            self.ir_value = arith.xori(
                self.operand_a.ir_value, self.operand_b.ir_value, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


@with_operators(arith=False, bitwise=True, order=False)
class NotOp(BaseUnaryBitwiseOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        from euqalyptus import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaBool or cls is QoalaInteger

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        # There is no "bitwise negate" operation in arith, but we can xor with 0xFF
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand.can_evaluate_to(QoalaBool):
            bool_type = mlir_bool()
            true_op = arith.constant(value=True, result=bool_type, loc=source_location)
            self.ir_value = true_op
            self.ir_value = arith.xori(
                self.operand.ir_value, true_op, loc=source_location
            )
        elif self.operand.can_evaluate_to(QoalaInteger):
            ff_val = arith.constant(value=0xFFFFFFFF, result=i32(), loc=source_location)
            self.ir_value = ff_val
            self.ir_value = arith.xori(
                self.operand.ir_value, ff_val, loc=source_location
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


class BitwiseOperatorFactory:
    def __new__(cls, *operands, operation: str) -> QoalaExpression:  # type: ignore[misc]
        if operation in ["__and__", "__rand__"]:
            return AndOp(*operands)
        elif operation in ["__or__", "__ror__"]:
            return OrOp(*operands)
        elif operation in ["__xor__", "__rxor__"]:
            return XorOp(*operands)
        elif operation in ["__neg__", "__invert__"]:
            return NotOp(*operands)
        else:
            raise UnknownOperationError(f"Operation '{operation}' is not supported")
