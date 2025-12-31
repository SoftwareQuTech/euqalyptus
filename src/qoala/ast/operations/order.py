from abc import ABC
from dataclasses import dataclass
from typing import Optional

from qnet.ir import Context, Location

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.casts import IntToFloat
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaBool
from qoala.errors import WrongEvaluationTypeError, UnknownOperationError


@dataclass(init=False)
class BaseBinaryBoolOp(QoalaOperation, ABC):
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


# TODO - Do we need to inherit some operators on this type of value?
class EqualsOp(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Implement this!
        pass


# TODO - Do we need to inherit some operators on this type of value?
class GreaterThanOp(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Implement this!
        pass


# TODO - Do we need to inherit some operators on this type of value?
class GreaterThanOrEqualsOp(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Implement this!
        pass


# TODO - Do we need to inherit some operators on this type of value?
class LessThanOp(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Implement this!
        pass


# TODO - Do we need to inherit some operators on this type of value?
class LessThanOrEqualsOp(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_current_function(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Implement this!
        pass


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