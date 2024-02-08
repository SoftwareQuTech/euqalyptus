from abc import ABC, abstractmethod
from typing import Self, Optional

from qoala.types.classical import QoalaClassicalType, _Internal_Value_Type
from qoala.utils import as_int_when_value


@as_int_when_value
class IntegerType(QoalaClassicalType[_Internal_Value_Type], ABC):
    # Operations associated with all integer types
    @abstractmethod
    def add(self, other: Self) -> Self:
        ...

    @abstractmethod
    def subtract(self, other: Self) -> Self:
        ...

    @abstractmethod
    def multiply(self, other: Self) -> Self:
        ...

    @abstractmethod
    def divide(self, other: Self) -> Self:
        ...

    # Method used for operator overload
    def __add__(self, other: Self) -> Self:
        return self.add(other)

    def __sub__(self, other: Self) -> Self:
        return self.subtract(other)

    def __mul__(self, other: Self) -> Self:
        return self.multiply(other)

    def __truediv__(self, other: Self) -> Self:
        return self.divide(other)


class SignedIntegerType(IntegerType[_Internal_Value_Type], ABC):
    ...


class UnsignedIntegerType(IntegerType[_Internal_Value_Type], ABC):
    ...


# TODO - Change the `int` parametric type when implementing
#        the internal representation.
# TODO - Expose the symbol of the internal representation
#        of this type
class Int32(SignedIntegerType[int]):
    """
    Class used to represent a `signed integer` of 32 bits
    """
    interval_value: int

    def __init__(
            self,
            immediate: int = 0,
            other_int32: Optional[Self] = None,
            # TODO - The next arguments are used when creating an Int32 from other types
    ):
        # TODO - Implement the internal representation and storage of the Int32
        self.interval_value = immediate
        if other_int32 is not None:
            self.interval_value = other_int32.interval_value

    def _get_value(self) -> int:
        # TODO - Implement
        return self.interval_value

    def add(self, other: Self) -> Self:
        # TODO - Implement
        pass

    def subtract(self, other: Self) -> Self:
        # TODO - Implement
        pass

    def multiply(self, other: Self) -> Self:
        # TODO - Implement
        pass

    def divide(self, other: Self) -> Self:
        # TODO - Implement
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
    interval_value: int

    def __init__(
            self,
            immediate: int = 0,
            other_uint32: Optional[Self] = 0,
            # TODO - The next arguments are used when creating an UInt32 from other types
    ):
        # TODO - Implement the internal representation and storage of the UInt32
        pass

    def _get_value(self) -> int:
        # TODO - Implement
        pass

    def add(self, other: Self) -> Self:
        # TODO - Implement
        pass

    def subtract(self, other: Self) -> Self:
        # TODO - Implement
        pass

    def multiply(self, other: Self) -> Self:
        # TODO - Implement
        pass

    def divide(self, other: Self) -> Self:
        # TODO - Implement
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
