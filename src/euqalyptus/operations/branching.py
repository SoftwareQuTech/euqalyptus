from euqalyptus import QoalaExpression
from euqalyptus.ast.operations.branching import ConditionalBranching
from euqalyptus.ast.operations.order import (
    EqualsOp,
    NotEqualsOp,
    LessThanOp,
    LessThanOrEqualsOp,
    GreaterThanOp,
    GreaterThanOrEqualsOp,
)
from euqalyptus.ast.value import QoalaBool
from euqalyptus.errors import OperandMismatchError, NotBooleanArgumentError
from euqalyptus.types.classical.booleans import Bool
from euqalyptus.types.classical.floats import QoalaFloatingPointType
from euqalyptus.types.classical.integer import QoalaIntegerType
from euqalyptus.utils.debug_info import get_debug_info


class IfCondition:
    """Records a runtime-conditional branching region.

    Used as a context manager, ``IfCondition`` (alias ``if_cond``) opens a
    branching region whose body is gated on a boolean ``QoalaExpression``
    evaluated at runtime. The context-manager idiom is::

        with if_cond(some_bool) as (t, f):
            ...
            with t:
                ...
            with f:
                ...

    The ``t`` and ``f`` handles refer to the "then" and "else" arms of the
    branching node and are themselves context managers. Quantum values that
    need to survive the branch must be wrapped in
    :class:`~euqalyptus.types.quantum.ScopedQubit`, and classical values in
    :class:`~euqalyptus.types.classical.ScopedVar`, before either arm is
    entered. See [Branching](../sdk/branching.md) for a full walkthrough.

    Args:
        condition: A boolean ``QoalaExpression`` (for example, the result of
            comparing a received integer to a literal). Python ``bool``
            literals and integer/float literals are auto-promoted.

    Raises:
        NotBooleanArgumentError: If the supplied argument cannot evaluate to
            a ``QoalaBool``.
    """

    def __new__(cls, *args: QoalaExpression, **kwargs):
        if len(args) >= 1:
            condition_value = cls._materialize_immediate(args[0])
            if condition_value.can_evaluate_to(QoalaBool):
                kwargs["condition"] = condition_value
            else:
                raise NotBooleanArgumentError("if_cond")
        return ConditionalBranching(**kwargs)

    @classmethod
    def _materialize_immediate(cls, arg: QoalaExpression | int | float):
        if isinstance(arg, QoalaExpression):
            return arg
        from euqalyptus.ast.value import QoalaNumericValue

        return QoalaNumericValue.from_immediate(arg, get_debug_info())

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
    """Branches when two operands are equal.

    Alias: ``if_eq``. Equivalent to ``if_cond(lhs == rhs)`` but recorded as a
    single ``EqualsOp`` node, which keeps the comparison explicit in HIR and
    can be picked up by downstream rewrites.

    Args:
        *operands: Exactly two values to compare. Each operand may be a
            ``QoalaIntegerType``, a ``QoalaFloatingPointType``, or a Python
            ``int`` / ``float`` literal (auto-promoted).

    Raises:
        OperandMismatchError: If fewer than two operands are supplied.
    """

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
        super().__init__(*operands)  # type: ignore[arg-type]


class IfNeq(IfCondition):
    """Branches when two operands are not equal.

    Alias: ``if_neq``. Equivalent to ``if_cond(lhs != rhs)`` but recorded as a
    single ``NotEqualsOp`` node.

    Args:
        *operands: Exactly two values to compare. Each operand may be a
            ``QoalaIntegerType``, a ``QoalaFloatingPointType``, or a Python
            ``int`` / ``float`` literal (auto-promoted).

    Raises:
        OperandMismatchError: If fewer than two operands are supplied.
    """

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
        super().__init__(*operands)  # type: ignore[arg-type]


class IfLt(IfCondition):
    """Branches when the first operand is strictly less than the second.

    Alias: ``if_lt``. Equivalent to ``if_cond(lhs < rhs)`` but recorded as a
    single ``LessThanOp`` node.

    Args:
        *operands: Exactly two values to compare. Each operand may be a
            ``QoalaIntegerType``, a ``QoalaFloatingPointType``, or a Python
            ``int`` / ``float`` literal (auto-promoted).

    Raises:
        OperandMismatchError: If fewer than two operands are supplied.
    """

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
        super().__init__(*operands)  # type: ignore[arg-type]


class IfLe(IfCondition):
    """Branches when the first operand is less than or equal to the second.

    Alias: ``if_le``. Equivalent to ``if_cond(lhs <= rhs)`` but recorded as a
    single ``LessThanOrEqualsOp`` node.

    Args:
        *operands: Exactly two values to compare. Each operand may be a
            ``QoalaIntegerType``, a ``QoalaFloatingPointType``, or a Python
            ``int`` / ``float`` literal (auto-promoted).

    Raises:
        OperandMismatchError: If fewer than two operands are supplied.
    """

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
        super().__init__(*operands)  # type: ignore[arg-type]


class IfGt(IfCondition):
    """Branches when the first operand is strictly greater than the second.

    Alias: ``if_gt``. Equivalent to ``if_cond(lhs > rhs)`` but recorded as a
    single ``GreaterThanOp`` node.

    Args:
        *operands: Exactly two values to compare. Each operand may be a
            ``QoalaIntegerType``, a ``QoalaFloatingPointType``, or a Python
            ``int`` / ``float`` literal (auto-promoted).

    Raises:
        OperandMismatchError: If fewer than two operands are supplied.
    """

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
        super().__init__(*operands)  # type: ignore[arg-type]


class IfGe(IfCondition):
    """Branches when the first operand is greater than or equal to the second.

    Alias: ``if_ge``. Equivalent to ``if_cond(lhs >= rhs)`` but recorded as a
    single ``GreaterThanOrEqualsOp`` node.

    Args:
        *operands: Exactly two values to compare. Each operand may be a
            ``QoalaIntegerType``, a ``QoalaFloatingPointType``, or a Python
            ``int`` / ``float`` literal (auto-promoted).

    Raises:
        OperandMismatchError: If fewer than two operands are supplied.
    """

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
        super().__init__(*operands)  # type: ignore[arg-type]


if_cond = IfCondition
if_eq = IfEq
if_neq = IfNeq
if_lt = IfLt
if_le = IfLe
if_ge = IfGe
if_gt = IfGt
