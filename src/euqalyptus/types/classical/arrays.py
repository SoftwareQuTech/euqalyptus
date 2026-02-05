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
        """
        Appends the given element to the array.

        Parameters
        ----------
        new_element: _Qoala_Base_Type | _Native_Base_Type
            the new element to append. Can either be a python type or a qoala type,
            but it must be consistent with the array you are trying to append to (i.e.
            it is not possible to append a float or QoalaFloat to an IntArray)

        Returns
        -------
        None
        """
        # Nothing to do here
        pass

    def __getitem__(self, item) -> _Qoala_Base_Type:  # type: ignore[empty-body]
        """
        "Brackets" operator for the qoala arrays. This method allows using qoala arrays
        using the indexing operator int the same way as an ordinary python array:
        array = IntArray(10, 20, 30)
        value = array[1] ## This access is allowed by this method
        """
        pass

    # Arrays are fixed-length by default (unless you use `store`)
    # so there is no __setitem__ overload


class IntArray(_Array[Int, int]):
    """
    An immutable array of 32 bits-wide integers. By immutable, it means that the size
    of the array *cannot* be changed, and the values stored in the array cannot be
    changed either
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
        """
        Creates a new IntArray instance with the given elements

        Parameters
        ----------
        elements:
            the elements to put in the array. The creation of the array will perform a
            type check to avoid inserting invalid values in the array (e.g. a float)
        base : QoalaArray
            an optional base array to create *a shallow copy* from. If this parameter
            is given in addition to any elements, the resulting array will contain
            *first* the same values of the base array, and then all the new elements given.
        """
        # Nothing to do here
        pass


class FloatArray(_Array[Float, float]):
    """
    An immutable array of 32 bits-wide single precision floating point values. By immutable,
    it means that the size of the array *cannot* be changed, and the values stored in the
    array cannot be changed either
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
        """
        Creates a new FloatArray instance with the given elements

        Parameters
        ----------
        elements:
            the elements to put in the array. The creation of the array will perform a
            type check to avoid inserting invalid values in the array (e.g. a int)
        base : QoalaArray
            an optional base array to create *a shallow copy* from. If this parameter
            is given in addition to any elements, the resulting array will contain
            *first* the same values of the base array, and then all the new elements given.
        """
        # Nothing to do here
        pass
