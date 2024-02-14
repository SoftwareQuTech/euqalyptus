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
    width: int
    signedness: Signedness
    value: _T

    @classmethod
    def _create_expression(cls, clazz: Type[_cls], operand_a: QoalaExpression, operand_b: QoalaExpression):
        return clazz(operand_a, operand_b)


class QoalaInteger(QoalaValue[int]):
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
        return super()._create_expression(Add, self, other)

    def subtract(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Subtract
        return super()._create_expression(Subtract, self, other)

    def multiply(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Multiply
        return super()._create_expression(Multiply, self, other)

    def divide(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Divide
        return super()._create_expression(Divide, self, other)

    # Method used for operator overload
    def __add__(self, other: Self) -> Self:
        return self.add(other)

    def __sub__(self, other: Self) -> Self:
        return self.subtract(other)

    def __mul__(self, other: Self) -> Self:
        return self.multiply(other)

    def __truediv__(self, other: Self) -> Self:
        return self.divide(other)


class QoalaFloat(QoalaValue[float]):
    def __init__(self, value: _T, width: int, signedness: Signedness, other: Optional[Self] = None):
        if other is not None:
            self.width = other.width
            self.signedness = other.signedness
            self.value = other.value
        else:
            self.width = width
            self.signedness = signedness
            self.value = value

    # Operations associated with all float types:
    def add(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Add
        return super()._create_expression(Add, self, other)

    def subtract(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Subtract
        return super()._create_expression(Subtract, self, other)

    def multiply(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Multiply
        return super()._create_expression(Multiply, self, other)

    def divide(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Divide
        return super()._create_expression(Divide, self, other)

    # Method used for operator overload
    def __add__(self, other: Self) -> Self:
        return self.add(other)

    def __sub__(self, other: Self) -> Self:
        return self.subtract(other)

    def __mul__(self, other: Self) -> Self:
        return self.multiply(other)

    def __truediv__(self, other: Self) -> Self:
        return self.divide(other)


class QoalaMeasure(QoalaValue[int]):
    pass
