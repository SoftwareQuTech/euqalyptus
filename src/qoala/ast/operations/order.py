from abc import ABC
from dataclasses import dataclass
from typing import Optional

from qnet.dialects import arith
from qnet.dialects.arith import CmpIPredicate, CmpFPredicate
from qnet.ir import Context, Location

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.casts import IntToFloat
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaBool
from qoala.errors import WrongEvaluationTypeError, UnknownOperationError


@dataclass(init=False)
class BaseBinaryOrderOp(QoalaOperation, ABC):
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

    def _compile_with_predicate(
        self, ctx: Context, int_predicate: CmpIPredicate, float_predicate: CmpFPredicate
    ) -> None:
        # We can assume that both operands evaluate to the same type, since the constructor
        # in the super class will insert an upcast if needed
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self.ir_value = arith.cmpi(
                predicate=int_predicate,
                lhs=self.operand_a.ir_value,
                rhs=self.operand_b.ir_value,
                loc=source_location,
            )
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self.ir_value = arith.cmpf(
                predicate=float_predicate,
                lhs=self.operand_a.ir_value,
                rhs=self.operand_b.ir_value,
                loc=source_location,
            )
        else:
            raise WrongEvaluationTypeError(
                f"When creating an operation of type '{self.__class__.__name__}', "
                f"the operands cannot be evaluated to any valid value."
            )


# TODO - Do we need to inherit some operators on this type of value?
class EqualsOp(BaseBinaryOrderOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # When comparing floats, there are 2 versions of the comparison: OGE and UGE
        # * OGE: *ORDERED* greater or equal than.
        # * UGE: *UNORDERED* greater or equal than.
        # - Unordered comparison will return "unordered" if one of the operands is Nan.
        # - Ordered comparison will *fail* is one of the operands is NaN
        # - No other differences apart from that.
        self._compile_with_predicate(
            ctx, arith.CmpIPredicate.eq, arith.CmpFPredicate.OEQ
        )


# TODO - Do we need to inherit some operators on this type of value?
class NotEqualsOp(BaseBinaryOrderOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # When comparing floats, there are 2 versions of the comparison: OGE and UGE
        # * OGE: *ORDERED* greater or equal than.
        # * UGE: *UNORDERED* greater or equal than.
        # - Unordered comparison will return "unordered" if one of the operands is Nan.
        # - Ordered comparison will *fail* is one of the operands is NaN
        # - No other differences apart from that.
        self._compile_with_predicate(
            ctx, arith.CmpIPredicate.ne, arith.CmpFPredicate.ONE
        )

# TODO - Do we need to inherit some operators on this type of value?
class GreaterThanOp(BaseBinaryOrderOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # When comparing floats, there are 2 versions of the comparison: OGE and UGE
        # * OGE: *ORDERED* greater or equal than.
        # * UGE: *UNORDERED* greater or equal than.
        # - Unordered comparison will return "unordered" if one of the operands is Nan.
        # - Ordered comparison will *fail* is one of the operands is NaN
        # - No other differences apart from that.
        self._compile_with_predicate(
            ctx, arith.CmpIPredicate.sgt, arith.CmpFPredicate.OGT
        )


# TODO - Do we need to inherit some operators on this type of value?
class GreaterThanOrEqualsOp(BaseBinaryOrderOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # When comparing floats, there are 2 versions of the comparison: OGE and UGE
        # * OGE: *ORDERED* greater or equal than.
        # * UGE: *UNORDERED* greater or equal than.
        # - Unordered comparison will return "unordered" if one of the operands is Nan.
        # - Ordered comparison will *fail* is one of the operands is NaN
        # - No other differences apart from that.
        self._compile_with_predicate(
            ctx, arith.CmpIPredicate.sge, arith.CmpFPredicate.OGE
        )


# TODO - Do we need to inherit some operators on this type of value?
class LessThanOp(BaseBinaryOrderOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # When comparing floats, there are 2 versions of the comparison: OGE and UGE
        # * OGE: *ORDERED* greater or equal than.
        # * UGE: *UNORDERED* greater or equal than.
        # - Unordered comparison will return "unordered" if one of the operands is Nan.
        # - Ordered comparison will *fail* is one of the operands is NaN
        # - No other differences apart from that.
        self._compile_with_predicate(
            ctx, arith.CmpIPredicate.slt, arith.CmpFPredicate.OLT
        )


# TODO - Do we need to inherit some operators on this type of value?
class LessThanOrEqualsOp(BaseBinaryOrderOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # When comparing floats, there are 2 versions of the comparison: OGE and UGE
        # * OGE: *ORDERED* greater or equal than.
        # * UGE: *UNORDERED* greater or equal than.
        # - Unordered comparison will return "unordered" if one of the operands is Nan.
        # - Ordered comparison will *fail* is one of the operands is NaN
        # - No other differences apart from that.
        self._compile_with_predicate(
            ctx, arith.CmpIPredicate.sle, arith.CmpFPredicate.OLE
        )


class OrderOperatorFactory:
    def __new__(cls, *operands, operation: str) -> QoalaExpression:
        if operation in ["__eq__"]:
            return EqualsOp(*operands)
        elif operation in ["__gt__"]:
            return GreaterThanOp(*operands)
        elif operation in ["__ge__"]:
            return GreaterThanOrEqualsOp(*operands)
        elif operation in ["__lt__"]:
            return LessThanOp(*operands)
        elif operation in ["__le__"]:
            return LessThanOrEqualsOp(*operands)
        else:
            raise UnknownOperationError(f"Operation '{operation}' is not supported")
