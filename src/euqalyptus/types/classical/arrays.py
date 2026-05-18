from typing import Generic, TypeVar, Type

from euqalyptus.ast.value import QoalaArray, QoalaExpression, QoalaInteger
from euqalyptus.errors import InvalidArrayArgumentError
from euqalyptus.types.classical import QoalaClassicalType, Float, Double, Int, Int32

_Qoala_Base_Type = TypeVar("_Qoala_Base_Type", bound=QoalaClassicalType)
_Native_Base_Type = TypeVar("_Native_Base_Type", int, float)


class _Array(Generic[_Qoala_Base_Type, _Native_Base_Type]):
    """
    Internal class used to group all the common behavior of numeric arrays
    """

    def __new__(cls, *elements, **kwargs):
        return QoalaArray[_Qoala_Base_Type, _Native_Base_Type](*elements, **kwargs)

    @staticmethod
    def _assert_elements(*elements: QoalaExpression, base_type: Type, array_type: Type):
        # Here we can assert that the elements are expressions
        # whether they can evaluate to a Double or not, is a semantic check
        if any(
            not isinstance(element, (base_type, QoalaExpression))
            for element in elements
        ):
            raise InvalidArrayArgumentError(array_type.__name__, base_type.__name__)

    def store(self, new_element: _Qoala_Base_Type | _Native_Base_Type) -> None:
        """Append an element to the array.

        Args:
            new_element: The new element to append. Either a Python
                native value (``int`` / ``float``) or a Qoala-typed
                value (``Int``, ``Float``, …); the element type must
                match the array's element type. Appending a float (or
                ``QoalaFloat``) to an ``IntArray`` raises an error.
        """
        # Nothing to do here
        pass

    def __getitem__(self, item) -> _Qoala_Base_Type:  # type: ignore[empty-body]
        """Index into the array.

        Enables ordinary Python indexing syntax on a Qoala array. For
        example, ``array[1]`` on an ``IntArray(10, 20, 30)`` records
        an access at index ``1``.

        Args:
            item: The index, either a Python ``int`` literal or a
                Qoala integer-typed value recorded earlier.

        Returns:
            A value of the array's element type, carrying the recorded
            indexed access.
        """
        pass

    # Arrays are fixed-length by default (unless you use `store`)
    # so there is no __setitem__ overload


class IntArray(_Array[Int, int]):
    """An immutable fixed-length array of 32-bit signed integers.

    The array is *immutable* in two senses: its length is fixed at
    construction time, and the values it stores cannot be reassigned
    in place. Use :meth:`_Array.store` to append (which extends the
    array) and ``array[i]`` to read.

    Args:
        *elements: The initial elements of the array. Each element must
            be either a Python ``int`` literal or a Qoala
            integer-typed value (``Int``, ``Int32``, …). Mixing
            element types — for instance passing a ``float`` — raises
            :class:`InvalidArrayArgumentError`.
        base: An optional existing :class:`QoalaArray` to shallow-copy
            from. When provided in addition to positional elements,
            the resulting array contains the values of ``base``
            followed by the new ``elements``.

    Raises:
        InvalidArrayArgumentError: If any element is not consistent
            with the integer base type.
    """

    def __new__(cls, *elements, **kwargs):
        kwargs["base_type"] = int
        kwargs["base_size"] = 32
        if "length" not in kwargs:
            kwargs["length"] = 0
        if "base" in kwargs:
            kwargs["base_clone"] = kwargs["base"]
            del kwargs["base"]
        else:
            kwargs["base_clone"] = None
        _Array._assert_elements(*elements, base_type=int, array_type=IntArray)
        return super().__new__(cls, *elements, **kwargs)  # type: ignore[arg-type]

    def __init__(
        self, *elements: Int | Int32 | int, base: QoalaArray[Int, int] | None = None
    ):
        # Nothing to do here
        pass


class FloatArray(_Array[Float, float]):
    """An immutable fixed-length array of 32-bit floating-point values.

    Like :class:`IntArray`, but with single-precision floating-point
    elements. Length is fixed at construction time and values cannot
    be reassigned in place; use :meth:`_Array.store` to append and
    ``array[i]`` to read.

    Args:
        *elements: The initial elements of the array. Each element must
            be either a Python ``float`` literal or a Qoala
            floating-point–typed value (``Float``, ``Double``).
            Passing an ``int`` raises :class:`InvalidArrayArgumentError`.
        base: An optional existing :class:`QoalaArray` to shallow-copy
            from. When provided in addition to positional elements,
            the resulting array contains the values of ``base``
            followed by the new ``elements``.

    Raises:
        InvalidArrayArgumentError: If any element is not consistent
            with the floating-point base type.
    """

    def __new__(cls, *elements, **kwargs):
        kwargs["base_type"] = float
        kwargs["base_size"] = 32
        if "length" not in kwargs:
            kwargs["length"] = 0
        if "base" in kwargs:
            kwargs["base_clone"] = kwargs["base"]
            del kwargs["base"]
        else:
            kwargs["base_clone"] = None
        _Array._assert_elements(*elements, base_type=float, array_type=FloatArray)
        return super().__new__(cls, *elements, **kwargs)  # type: ignore[arg-type]

    def __init__(
        self,
        *elements: Float | Double | float,
        base: QoalaArray[Float, float] | None = None,
    ):
        # Nothing to do here
        pass
