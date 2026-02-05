from typing import Optional

from typing_extensions import Self

from euqalyptus.ast.value import QoalaInteger, Signedness
from euqalyptus.errors import NotUnsignedIntegerArgumentError, NotIntegerArgumentError
from euqalyptus.types.classical import (
    QoalaClassicalType,
    _Internal_Value_Type,
    NumericOperandsOverload,
)


class QoalaIntegerType(
    QoalaClassicalType[_Internal_Value_Type], NumericOperandsOverload
):
    pass


class _SignedIntegerType(QoalaIntegerType[_Internal_Value_Type]):
    pass


class _UnsignedIntegerType(QoalaIntegerType[_Internal_Value_Type]):
    pass


class Int32(_SignedIntegerType[int]):
    """
    Represents a `signed integer` of 32 bits
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
                raise NotIntegerArgumentError(Int32.__name__)
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
        """
        Creates a new instance of a 32 bits-wide *signed* integer.

        Parameters
        ----------
        immediate: int
            the immediate value (as a python integer) for the new qoala integer. If not given
            this value defaults to '0'
        other: Int32
            if given, the newly created integer will contain a copy of the value passed here.
            Using this argument has the effect to create *a totally new integer instance*, but
            containing the same value as the given argument. Use this method to create "deep
            copies" of an integer.
        """
        # Nothing to do here
        pass


Int = Int32


class UInt32(_UnsignedIntegerType[int]):
    """
    Represents an `unsigned integer` of 32 bits
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
                raise NotIntegerArgumentError(UInt32.__name__)
            if args[0] < 0:
                raise NotUnsignedIntegerArgumentError(UInt32.__name__)
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
        # TODO - The next arguments are used when creating an UInt32 from other types
    ):
        """
        Creates a new instance of a 32 bits-wide *unsigned* integer.

        Parameters
        ----------
        immediate: int
            the immediate value (as a python integer) for the new qoala integer. If not given
            this value defaults to '0'
        other: UInt32
            if given, the newly created integer will contain a copy of the value passed here.
            Using this argument has the effect to create *a totally new integer instance*, but
            containing the same value as the given argument. Use this method to create "deep
            copies" of an integer.
        """
        # Nothing to do here
        pass


class Bit(QoalaClassicalType[int]):
    """
    Integer value that represents the returned value form measuring a qubit.
    This integer can `only` have the value `0` or `1`, which is the potential
    returned values from measuring a qubit.
    This class does not support operations like "add", since it is not how
    these operations are defined for the result of a measurement.
    IMPORTANT: Despite a programmer could use the 'Bit' type of the
    qoala.types.classical.integer package to declare and create a value of this
    type, this is a use case that it is *not* encouraged.
    """

    pass
