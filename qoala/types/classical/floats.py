from abc import ABC
from typing import Self

from deprecated import deprecated

from qoala.ast.value import QoalaFloat
from qoala.types.classical import QoalaClassicalType, _Internal_Value_Type


class QoalaFloatingPointType(QoalaClassicalType[_Internal_Value_Type], ABC):
    # We overload the operators, so IDEs do not get confused because of the
    # dynamic type of floats, so instances of this class "can use" the overloaded
    # operator. This is because the constructor of this class (method __new__)
    # returns a QoalaExpression type, rather than a Float/Double instance
    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __truediv__(self, other):
        pass


# TODO - Change the `float` parametric type when implementing
#        the internal representation.
# TODO - Expose the symbol of the internal representation
#        of this type
class Float(QoalaFloatingPointType[float]):
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


@deprecated(reason="Double type is not supported by Qoala.\n"
                   "For this reason the usage of this type is not encouraged.\n"
                   "To maintain compatibility, this type will be implemented as\n"
                   "a synonym of the 'Float' type.")
class Double(Float):
    pass
