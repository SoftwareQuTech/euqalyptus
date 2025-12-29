from dataclasses import dataclass
from abc import ABC

from qnet._mlir_libs._mlir.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
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

    def compile(self, ctx: Context) -> None:
        pass


@with_bool_operators
class Or(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context) -> None:
        # TODO - Implement similar to Integer operations!
        pass


@with_bool_operators
class Xor(BaseBinaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context) -> None:
        # TODO - Implement similar to Integer operations!
        pass


@with_bool_operators
class Not(BaseUnaryBoolOp):
    def __init__(self, *operands: QoalaExpression):
        super().__init__(*operands)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaBool

    def compile(self, ctx: Context) -> None:
        # TODO - Implement similar to Integer operations!
        pass


class BooleanOperatorFactory:
    def __new__(cls, *operands, operation: str) -> QoalaExpression:
        # TODO - Change the exception raising and create the respective classes that model
        #  the bool operation in the AST
        from qoala.errors import OperationNotYetImplementedError

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
