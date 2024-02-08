from abc import ABC, abstractmethod
from typing import Self

from qoala.types.classical import QoalaClassicalType, _Internal_Value_Type


class FloatingPointType(QoalaClassicalType[_Internal_Value_Type], ABC):
    # Operations associated with all float types
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


# TODO - Change the `float` parametric type when implementing
#        the internal representation.
# TODO - Expose the symbol of the internal representation
#        of this type
# FIXME - This type might not be needed. According to the specification
#         QoalaHIR only supports the `f32` type (a.k.a. doubles)
class Float(FloatingPointType[float]):
    internal_value: float

    def __init__(
            self,
            immediate: float = 0,
            other_float: Self = 0,
            # TODO - The next arguments are used when creating a Float from other types
    ):
        # TODO - Implement the internal representation and storage of the Float
        pass

    def _get_value(self) -> _Internal_Value_Type:
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


# TODO - Change the `float` parametric type when implementing
#        the internal representation.
# TODO - Expose the symbol of the internal representation
#        of this type
class Double(FloatingPointType[float]):
    internal_representation: float

    def __init__(
            self,
            immediate: float = 0,
            other_double: Self = 0,
            # TODO - The next arguments are used when creating a Double from other types
    ):
        # TODO - Implement the internal representation and storage of the Double
        pass

    def _get_value(self) -> _Internal_Value_Type:
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
