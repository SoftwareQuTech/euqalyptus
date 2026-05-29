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
    """A 32-bit signed integer.

    Constructing an ``Int32`` inside a ``@QoalaProgram`` body records a
    new classical integer value of width 32 and signed signedness. The
    returned object supports the standard numeric and bitwise operators
    inherited from :class:`NumericOperandsOverload`.

    Args:
        immediate: A Python ``int`` literal that becomes the immediate
            value of the new integer. Defaults to ``0``.
        other: If provided, the new integer is initialized as a copy of
            ``other``'s value. Use this to deep-copy an existing
            integer into a fresh SSA value.

    Raises:
        NotIntegerArgumentError: If the positional ``immediate``
            argument is not a Python ``int``.
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
        # Nothing to do here
        pass


Int = Int32
"""Alias of :class:`Int32`. The recommended name for a 32-bit signed integer."""


class UInt32(_UnsignedIntegerType[int]):
    """A 32-bit unsigned integer.

    Constructing a ``UInt32`` inside a ``@QoalaProgram`` body records a
    new classical integer value of width 32 and unsigned signedness.
    The returned object supports the standard numeric and bitwise
    operators inherited from :class:`NumericOperandsOverload`.

    Args:
        immediate: A non-negative Python ``int`` literal that becomes
            the immediate value of the new integer. Defaults to ``0``.
        other: If provided, the new integer is initialized as a copy of
            ``other``'s value.

    Raises:
        NotIntegerArgumentError: If the positional ``immediate``
            argument is not a Python ``int``.
        NotUnsignedIntegerArgumentError: If the positional ``immediate``
            argument is negative.
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
        # Nothing to do here
        pass


class Bit(QoalaClassicalType[int]):
    """A single classical bit (the outcome of a qubit measurement).

    A ``Bit`` value can only take the values ``0`` or ``1`` — the
    possible outcomes of measuring a qubit. The class deliberately
    does *not* support arithmetic operations (such as ``+``): those
    are not meaningful semantics for a measurement result.

    Note:
        Although the class is exposed in
        ``euqalyptus.types.classical.integer``, you should rarely
        construct a ``Bit`` yourself. The canonical way to obtain one
        is to call ``q.measure()`` on a qubit, which returns a ``Bit``
        carrying the measurement outcome.
    """

    pass
