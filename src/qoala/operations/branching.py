from qoala import QoalaExpression
from qoala.ast.operations.branching import ConditionalBranching
from qoala.ast.operations.order import (
    EqualsOp,
    NotEqualsOp,
    LessThanOp,
    LessThanOrEqualsOp,
    GreaterThanOp,
    GreaterThanOrEqualsOp,
)
from qoala.ast.value import QoalaBool
from qoala.errors import OperandMismatchError, NotBooleanArgumentError
from qoala.types.classical.booleans import Bool
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.integer import QoalaIntegerType


class IfCondition:
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 1:
            condition_value = cls._materialize_immediate(args[0])
            if condition_value.can_evaluate_to(QoalaBool):
                kwargs["condition"] = condition_value
            else:
                raise NotBooleanArgumentError
        return ConditionalBranching(**kwargs)

    @classmethod
    def _materialize_immediate(cls, arg: QoalaExpression | int | float):
        if isinstance(arg, QoalaExpression):
            return arg
        from qoala.ast.value import QoalaNumericValue

        # TODO - Get the actual debug info somehow!
        return QoalaNumericValue.from_immediate(arg, None)

    def __init__(self, condition: Bool | bool):
        # Nothing to do here
        pass

    def __enter__(self):
        # Nothing to do here
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Nothing to do here
        pass


class IfEq(IfCondition):
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 2:
            lhs = cls._materialize_immediate(args[0])
            rhs = cls._materialize_immediate(args[1])
            kwargs["condition"] = EqualsOp(lhs, rhs)
        else:
            raise OperandMismatchError(
                f"Branching of type '{cls.__name__}' requires 2 arguments."
            )
        return ConditionalBranching(**kwargs)

    def __init__(
        self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float
    ):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfNeq(IfCondition):
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 2:
            lhs = cls._materialize_immediate(args[0])
            rhs = cls._materialize_immediate(args[1])
            kwargs["condition"] = NotEqualsOp(lhs, rhs)
        else:
            raise OperandMismatchError(
                f"Branching of type '{cls.__name__}' requires 2 arguments."
            )
        return ConditionalBranching(**kwargs)

    def __init__(
        self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float
    ):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfLt(IfCondition):
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 2:
            lhs = cls._materialize_immediate(args[0])
            rhs = cls._materialize_immediate(args[1])
            kwargs["condition"] = LessThanOp(lhs, rhs)
        else:
            raise OperandMismatchError(
                f"Branching of type '{cls.__name__}' requires 2 arguments."
            )
        return ConditionalBranching(**kwargs)

    def __init__(
        self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float
    ):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfLe(IfCondition):
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 2:
            lhs = cls._materialize_immediate(args[0])
            rhs = cls._materialize_immediate(args[1])
            kwargs["condition"] = LessThanOrEqualsOp(lhs, rhs)
        else:
            raise OperandMismatchError(
                f"Branching of type '{cls.__name__}' requires 2 arguments."
            )
        return ConditionalBranching(**kwargs)

    def __init__(
        self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float
    ):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfGt(IfCondition):
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 2:
            lhs = cls._materialize_immediate(args[0])
            rhs = cls._materialize_immediate(args[1])
            kwargs["condition"] = GreaterThanOp(lhs, rhs)
        else:
            raise OperandMismatchError(
                f"Branching of type '{cls.__name__}' requires 2 arguments."
            )
        return ConditionalBranching(**kwargs)

    def __init__(
        self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float
    ):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfGe(IfCondition):
    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 2:
            lhs = cls._materialize_immediate(args[0])
            rhs = cls._materialize_immediate(args[1])
            kwargs["condition"] = GreaterThanOrEqualsOp(lhs, rhs)
        else:
            raise OperandMismatchError(
                f"Branching of type '{cls.__name__}' requires 2 arguments."
            )
        return ConditionalBranching(**kwargs)

    def __init__(
        self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float
    ):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


if_cond = IfCondition
if_eq = IfEq
if_neq = IfNeq
if_lt = IfLt
if_le = IfLe
if_ge = IfGe
if_gt = IfGt
