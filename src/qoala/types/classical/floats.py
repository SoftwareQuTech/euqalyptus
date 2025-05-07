from typing_extensions import Self

from qoala.ast.value import QoalaFloat
from qoala.types.classical import (
    QoalaClassicalType,
    _Internal_Value_Type,
    _NumericOperandsOverload,
)


class QoalaFloatingPointType(
    QoalaClassicalType[_Internal_Value_Type], _NumericOperandsOverload
):
    pass


class Float(QoalaFloatingPointType[float]):
    """
    Represents a floating point value.
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
        immediate: float = 0,
        other: Self = 0,
        # TODO - The next arguments are used when creating a Float from other types
    ):
        # Nothing to do here
        pass


# the "Double" type is just a synonym of the "Float"
Double = Float
