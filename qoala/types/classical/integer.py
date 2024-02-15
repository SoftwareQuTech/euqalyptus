from abc import ABC
from typing import Self, Optional

from qoala.ast.value import QoalaInteger, Signedness
from qoala.types.classical import ClassicalType, _Internal_Value_Type, InvalidArgumentError
from qoala.utils import as_int_when_value


@as_int_when_value
class IntegerType(ClassicalType[_Internal_Value_Type], ABC):
    # We overload the operators, so IDEs do not get confused because of the
    # dynamic type of integers, so instances of this class "can use" the overloaded
    # operator. This is because the constructor of this class (method __new__)
    # returns a QoalaExpression type, rather than an Int/Int32/UInt32 instance
    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __truediv__(self, other):
        pass


class SignedIntegerType(IntegerType[_Internal_Value_Type], ABC):
    pass


class UnsignedIntegerType(IntegerType[_Internal_Value_Type], ABC):
    pass


class Int32(SignedIntegerType[int]):
    """
    Class used to represent a `signed integer` of 32 bits
    """

    def __new__(cls, *args, **kwargs):
        kwargs["width"] = 32
        kwargs["signedness"] = Signedness.SIGNED

        if "immediate" in kwargs:
            kwargs["value"] = kwargs["immediate"]
            del kwargs["immediate"]
        elif len(args) >= 1:
            kwargs["value"] = args[0]
            if not isinstance(args[0], int):
                raise InvalidArgumentError(f"'{Int32.__name__}' type only supports integer values")
        else:
            kwargs["value"] = 0

        if "other" in kwargs:
            assert isinstance(kwargs["other"], QoalaInteger)
            kwargs["value"] = kwargs["other"]
            del kwargs["other"]

        return QoalaInteger(**kwargs)

    def __init__(
            self,
            immediate: int = 0,
            other: Optional[Self] = None,
            # TODO - The next arguments are used when creating an Int32 from other types
    ):
        # Nothing to do here
        pass


Int = Int32


class UInt32(UnsignedIntegerType[int]):
    """
    Class used to represent a `signed integer` of 32 bits
    """

    def __new__(cls, *args, **kwargs):
        kwargs["width"] = 32
        kwargs["signedness"] = Signedness.UNSIGNED
        if "immediate" in kwargs:
            assert isinstance(kwargs["immediate"], int)
            kwargs["value"] = kwargs["immediate"]
            del kwargs["immediate"]
        elif len(args) >= 1:
            kwargs["value"] = args[0]
            if not isinstance(args[0], int):
                raise InvalidArgumentError(f"'{UInt32.__name__}' type only supports integer values")
            if args[0] < 0:
                raise InvalidArgumentError(f"'{UInt32.__name__}' type only supports positive integer values")
        else:
            kwargs["value"] = 0


        if "other" in kwargs:
            assert isinstance(kwargs["other"], QoalaInteger)
            kwargs["value"] = kwargs["other"]
            del kwargs["other"]

        return QoalaInteger(**kwargs)

    def __init__(
            self,
            immediate: int = 0,
            other: Optional[Self] = 0,
            # TODO - The next arguments are used when creating an UInt32 from other types
    ):
        # Nothing to do here
        pass


class Measure(ClassicalType[int]):
    """
    Integer value that represents the returned value form measuring a qubit.
    This integer can `only` have the value `0` or `1`, which is the potential
    returned values from measuring a qubit.
    This class does not support operations like "add", since it is not how
    these operations are defined for the result of a measurement.
    """
    pass
