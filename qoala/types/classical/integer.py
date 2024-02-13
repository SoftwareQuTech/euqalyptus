from abc import ABC
from typing import Self, Optional

from qoala.ast.value import QoalaInteger, Signedness
from qoala.types.classical import QoalaClassicalType, _Internal_Value_Type
from qoala.utils import as_int_when_value


@as_int_when_value
class IntegerType(QoalaClassicalType[_Internal_Value_Type], ABC):

    # We overload the operators, so IDEs do not get confused because of the
    # dynamic type of Int32, so instances of this class "can use" the overloaded
    # operator. This is because the constructor of this class (method __new__)
    # returns a QoalaExpression type, rather than an Int32 instance
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


# TODO - Change the `int` parametric type when implementing
#        the internal representation.
# TODO - Expose the symbol of the internal representation
#        of this type
class Int32(SignedIntegerType[int]):
    """
    Class used to represent a `signed integer` of 32 bits
    """

    def __new__(cls, *args, **kwargs):
        kwargs["width"] = 32
        kwargs["signedness"] = Signedness.SIGNED
        if kwargs["immediate"] is not None:
            kwargs["value"] = kwargs["immediate"]
            del kwargs["immediate"]
        elif args[0] is not None:
            kwargs["value"] = args[0]
        else:
            kwargs["value"] = 0
        int_expr = QoalaInteger(*kwargs)
        return int_expr

    def __init__(
            self,
            immediate: int = 0,
            other_int32: Optional[Self] = None,
            # TODO - The next arguments are used when creating an Int32 from other types
    ):
        # Nothing to do here
        pass


Int = Int32


# TODO - Change the `int` parametric type when implementing
#        the internal representation.
# TODO - Expose the symbol of the internal representation
#        of this type
class UInt32(UnsignedIntegerType[int]):
    """
    Class used to represent a `signed integer` of 32 bits
    """

    def __new__(cls, *args, **kwargs):
        kwargs["width"] = 32
        kwargs["signedness"] = Signedness.UNSIGNED
        if kwargs["immediate"] is not None:
            kwargs["value"] = kwargs["immediate"]
            del kwargs["immediate"]
        elif args[0] is not None:
            kwargs["value"] = args[0]
        else:
            kwargs["value"] = 0
        int_expr = QoalaInteger(*kwargs)
        return int_expr

    def __init__(
            self,
            immediate: int = 0,
            other_uint32: Optional[Self] = 0,
            # TODO - The next arguments are used when creating an UInt32 from other types
    ):
        # Nothing to do here
        pass


class Measure(QoalaClassicalType[int]):
    """
    Integer value that represents the returned value form measuring a qubit.
    This integer can `only` have the value `0` or `1`, which is the potential
    returned values from measuring a qubit.
    This class does not support operations like "add", since it is not how
    these operations are defined for the result of a measurement.
    """
    def _get_value(self) -> _Internal_Value_Type:
        # TODO - Implement
        pass
