from abc import ABC
from enum import Enum, auto
from typing import Generic, TypeVar, Self, Optional

from qoala.ast import QoalaExpression

_T = TypeVar("_T")


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
        instance = Add(self, other)
        return instance

    def subtract(self, other: QoalaExpression) -> QoalaExpression:
        pass

    def multiply(self, other: QoalaExpression) -> QoalaExpression:
        pass

    def divide(self, other: QoalaExpression) -> QoalaExpression:
        pass

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

    # Operations associated with all integer types:
    def add(self, other: QoalaExpression) -> QoalaExpression:
        from qoala.ast.operations.integer import Add
        instance = Add(self, other)
        return instance

    def subtract(self, other: QoalaExpression) -> QoalaExpression:
        pass

    def multiply(self, other: QoalaExpression) -> QoalaExpression:
        pass

    def divide(self, other: QoalaExpression) -> QoalaExpression:
        pass

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
