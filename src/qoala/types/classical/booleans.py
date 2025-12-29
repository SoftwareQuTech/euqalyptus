from typing import Optional, Self

from qoala.ast.value import QoalaBool
from qoala.errors import NotBooleanArgumentError
from qoala.types.classical import QoalaClassicalType, _BooleanOperandsOverload


class QoalaBooleanType(
    QoalaClassicalType[bool], _BooleanOperandsOverload
):
    pass


class Bool(QoalaBooleanType):
    def __new__(cls, *args, **kwargs):
        if "immediate" in kwargs:
            kwargs["value"] = kwargs["immediate"]
            del kwargs["immediate"]
        elif len(args) >= 1:
            kwargs["value"] = args[0]
            if not isinstance(args[0], int):
                raise NotBooleanArgumentError(Bool.__name__)
        else:
            kwargs["value"] = 0

        if "other" in kwargs:
            assert isinstance(kwargs["other"], QoalaBool)
            kwargs["value"] = kwargs["other"]
            del kwargs["other"]

        return QoalaBool(**kwargs)

    def __init__(
        self,
        immediate: bool = False,
        other: Optional[Self] = None
    ):
        """
        Creates a new instance of a 32 bits-wide *signed* integer.

        Parameters
        ----------
        immediate: bool
            the immediate value (as a python bool) for the new qoala boolean. If not given
            this value defaults to 'false'
        other: Bool
            if given, the newly created boolean will contain a copy of the value passed here.
            Using this argument has the effect to create *a totally new boolean instance*, but
            containing the same value as the given argument. Use this method to create "deep
            copies" of a boolean.
        """
        # Nothing to do here
        pass
