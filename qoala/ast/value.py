from abc import ABC
from enum import Enum, auto
from typing import Generic, TypeVar, Self, Optional, Type

from qoala.ast import QoalaExpression

_T = TypeVar("_T")
_cls = TypeVar("_cls", bound=QoalaExpression)


class Signedness(Enum):
    UNKNOWN = 0
    SIGNED = auto()
    UNSIGNED = auto()


class QoalaValue(ABC, QoalaExpression, Generic[_T]):
    """
    Class used to represent a value in the AST. Nodes of this type (i.e.
    subclasses) are usually the leaves of the AST.
    """

    @staticmethod
    def _create_expression_for_op(op_class: Type[_cls], operand_a: QoalaExpression, operand_b: QoalaExpression):
        return op_class(operand_a, operand_b)


class QoalaNumericValue(QoalaValue[_T], ABC):
    signedness: Signedness
    width: int
    value: _T


class QoalaInteger(QoalaNumericValue[int]):
    def __init__(self, value: _T, width: int, signedness: Signedness, other: Optional[Self] = None):
        if other is not None:
            self.width = other.width
            self.signedness = other.signedness
            self.value = other.value
        else:
            self.width = width
            self.signedness = signedness
            self.value = value

    # Operations associated with all integer types:
    def add(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Add
        return QoalaValue._create_expression_for_op(Add, self, other)

    def subtract(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Subtract
        return QoalaValue._create_expression_for_op(Subtract, self, other)

    def multiply(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Multiply
        return QoalaValue._create_expression_for_op(Multiply, self, other)

    def divide(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Divide
        return QoalaValue._create_expression_for_op(Divide, self, other)

    # Method used for operator overload
    def __add__(self, other: Self) -> Self:
        return self.add(other)

    def __sub__(self, other: Self) -> Self:
        return self.subtract(other)

    def __mul__(self, other: Self) -> Self:
        return self.multiply(other)

    def __truediv__(self, other: Self) -> Self:
        return self.divide(other)


class QoalaFloat(QoalaNumericValue[float]):
    def __init__(self, value: _T, width: int, other: Optional[Self] = None):
        if other is not None:
            self.width = other.width
            self.signedness = Signedness.UNKNOWN
            self.value = other.value
        else:
            self.width = width
            self.signedness = Signedness.UNKNOWN
            self.value = value

    # Operations associated with all float types:
    def add(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Add
        return QoalaValue._create_expression_for_op(Add, self, other)

    def subtract(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Subtract
        return QoalaValue._create_expression_for_op(Subtract, self, other)

    def multiply(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Multiply
        return QoalaValue._create_expression_for_op(Multiply, self, other)

    def divide(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Divide
        return QoalaValue._create_expression_for_op(Divide, self, other)

    # Method used for operator overload
    def __add__(self, other: Self) -> Self:
        return self.add(other)

    def __sub__(self, other: Self) -> Self:
        return self.subtract(other)

    def __mul__(self, other: Self) -> Self:
        return self.multiply(other)

    def __truediv__(self, other: Self) -> Self:
        return self.divide(other)


# FIXME - In the meantime, we will model arrays as if they were
#         values. We might want to reconsider this decision in
#         the future.
class QoalaArray(QoalaValue[_T]):
    def __init__(self, type, size):
        pass


class QoalaMeasure(QoalaValue[int]):
    pass
