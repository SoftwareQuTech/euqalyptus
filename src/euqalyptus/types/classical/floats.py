from typing_extensions import Self

from euqalyptus.ast.value import QoalaFloat
from euqalyptus.types.classical import (
    QoalaClassicalType,
    _Internal_Value_Type,
    NumericOperandsOverload,
)


class QoalaFloatingPointType(
    QoalaClassicalType[_Internal_Value_Type], NumericOperandsOverload
):
    pass


class Float(QoalaFloatingPointType[float]):
    """A 32-bit floating-point value.

    Constructing a ``Float`` inside a ``@QoalaProgram`` body records a
    new classical floating-point SSA value. The returned object
    supports the standard numeric operators inherited from
    :class:`NumericOperandsOverload`.

    Args:
        immediate: A Python ``float`` (or ``int``) literal that becomes
            the immediate value of the new float. Defaults to ``0.0``.
        other: If provided, the new value is initialized as a copy of
            ``other``.
    """

    def __new__(cls, *args, **kwargs):
        kwargs["width"] = 32

        if "immediate" in kwargs:
            assert isinstance(kwargs["immediate"], int)
            kwargs["value"] = kwargs["immediate"]
            del kwargs["immediate"]
        elif len(args) >= 1:
            kwargs["value"] = args[0]
        else:
            kwargs["value"] = 0

        if "other" in kwargs:
            assert isinstance(kwargs["other"], QoalaFloat)
            kwargs["value"] = kwargs["other"]
            del kwargs["other"]

        return QoalaFloat(**kwargs)

    def __init__(
        self,
        immediate: float = 0.0,
        other: Self = None,  # type: ignore[assignment]
        # TODO - The next arguments are used when creating a Float from other types
    ):
        # Nothing to do here
        pass


Double = Float
"""Alias of :class:`Float`. Provided for consistency with code that distinguishes
``float`` and ``double`` width; both point at the same 32-bit floating-point type."""
