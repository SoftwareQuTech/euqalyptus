from abc import ABC, abstractmethod
from typing import Self


class QoalaClassicalType(ABC):
    @abstractmethod
    def get_value(self) -> Self:
        ...


class IntegerType(QoalaClassicalType, ABC):
    @abstractmethod
    def get_value(self) -> Self:
        ...

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


class SignedIntegerType(IntegerType, ABC):
    ...


class UnsignedIntegerType(IntegerType, ABC):
    ...


class Int32(SignedIntegerType):
    """
    Class used to represent a `signed integer` of 32 bits
    """

    def __init__(
            self,
            immediate: int = 0,
            other_int32: Self = 0,
            # TODO - The next arguments are used when creating an Int32 from other types
    ):
        # TODO - Implement the internal representation and storage of the Int32
        pass

    def get_value(self) -> Self:
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
