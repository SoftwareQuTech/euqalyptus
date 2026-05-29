from typing import Optional

from typing_extensions import Self

from euqalyptus.ast.value import QoalaBool
from euqalyptus.errors import NotBooleanArgumentError
from euqalyptus.types.classical import QoalaClassicalType, BitwiseOperandsOverload


class QoalaBooleanType(QoalaClassicalType[bool], BitwiseOperandsOverload):
    pass


class Bool(QoalaBooleanType):
    """A classical boolean value.

    Constructing a ``Bool`` inside a ``@QoalaProgram`` body records a
    new classical boolean SSA value. Booleans are typically used as
    branching predicates (the condition of an ``if_cond(...)`` block)
    and support the bitwise operators inherited from
    :class:`BitwiseOperandsOverload`.

    Args:
        immediate: A Python ``bool`` (or ``int``) literal that becomes
            the immediate value of the new boolean. Defaults to
            ``False``.
        other: If provided, the new boolean is initialized as a copy
            of ``other``.

    Raises:
        NotBooleanArgumentError: If the positional ``immediate``
            argument is not coercible to a boolean.
    """

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

    def __init__(self, immediate: bool = False, other: Optional[Self] = None):
        # Nothing to do here
        pass
