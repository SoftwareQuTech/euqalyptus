from typing import TypeVar, Generic

from qoala.types import QoalaType

_Internal_Value_Type = TypeVar("_Internal_Value_Type")


class QoalaClassicalType(Generic[_Internal_Value_Type], QoalaType):
    """
    Base class that represents an integer in the classical computation
    model. Similarly, an instance of this class represents a classical
    value of the given type.
    Each subtype of this class can define the operations that can be
    applied to the type. In this sense, and to keep the type closed,
    any operation applied on 1 or more instances (values) of this class
    (type) `will yield a new instance` (value) of the same type.
    """

    pass


class _NumericOperandsOverload:
    # We overload the dunder methods operators, so IDEs do not get confused because of
    # the dynamic type of integers, so instances of this class "can use" the overloaded
    # operator. This is because the constructor of the concrete types return an instance
    # of a subclass of QoalaExpression, rather than an Int/Int32/UInt32 instance
    def __add__(self, other):
        pass

    def __radd__(self, other):
        pass

    def __iadd__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __rsub__(self, other):
        pass

    def __isub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __rmul__(self, other):
        pass

    def __imul__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __rtruediv__(self, other):
        pass

    def __itruediv__(self, other):
        pass

    # Overload of numeric operands that yield booleans
    def __eq__(self, other):
        pass

    def __ne__(self, other):
        pass

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass

    def __le__(self, other):
        pass

    def __ge__(self, other):
        pass


class _BooleanOperandsOverload:
    # We overload the dunder methods operators, so IDEs do not get confused because of
    # the dynamic type of booleans, so instances of this class "can use" the overloaded
    # operator. This is because the constructor of the concrete types return an instance
    # of a subclass of QoalaExpression, rather than a Boolean instance
    def __and__(self, other):
        pass

    def __or__(self, other):
        pass


from .integer import Int, Int32, UInt32, Bit
from .floats import Float, Double
from .arrays import IntArray, FloatArray
