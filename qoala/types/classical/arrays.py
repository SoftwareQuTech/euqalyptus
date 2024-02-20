from typing import Generic, TypeVar, Optional, Sized, Union, Type

from qoala.ast.value import QoalaArray, QoalaExpression
from qoala.types.classical import ClassicalType
from qoala.types.classical.errors import InvalidArgumentError
from qoala.types.classical.floats import Double
from qoala.types.classical.integer import Int

_Qoala_Base_Type = TypeVar("_Qoala_Base_Type", bound=ClassicalType)
_Native_Base_Type = TypeVar("_Native_Base_Type", int, float)


class _Array(Generic[_Qoala_Base_Type, _Native_Base_Type], Sized):
    def __new__(cls, *elements, **kwargs):
        return QoalaArray[_Native_Base_Type](*elements, **kwargs)

    @staticmethod
    def _assert_elements(
            *elements: QoalaExpression,
            base_type: Type,
            array_type: Type
    ):
        # Here we can assert that the elements are expressions
        # whether they can evaluate to a Double or not, is a semantic check
        if any(not isinstance(element, (base_type, QoalaExpression)) for element in elements):
            raise InvalidArgumentError(f"Array of type '{array_type.__name__}' "
                                       f"can only hold values of type '{base_type.__name__}'")
    def store(self, new_element: _Qoala_Base_Type | _Native_Base_Type) -> None:
        # Nothing to do here
        pass

    def __repr__(self) -> str:
        pass

    def __len__(self) -> int:
        pass

    def __getitem__(self, item) -> _Qoala_Base_Type:
        pass

    # Arrays are fixed-length by default (unless you use `store`)
    # so there is no __setitem__ overload


class IntArray(_Array[Int, int]):
    def __new__(cls, *elements, **kwargs):
        kwargs["base_type"] = int
        kwargs["base_size"] = 32
        if "length" not in kwargs:
            kwargs["length"] = 0
        _Array._assert_elements(*elements, base_type=int, array_type=IntArray)
        return super().__new__(cls, *elements, **kwargs)

    def __init__(
            self,
            *elements: Union[_Qoala_Base_Type, int],
            other_array: Optional[QoalaArray[int]] = None
    ):
        # Nothing to do here
        pass


class FloatArray(_Array[Double, float]):
    def __new__(cls, *elements, **kwargs):
        kwargs["base_type"] = float
        kwargs["base_size"] = 32
        if "length" not in kwargs:
            kwargs["length"] = 0
        _Array._assert_elements(*elements, base_type=float, array_type=FloatArray)
        return super().__new__(cls, *elements, **kwargs)

    def __init__(
            self,
            *elements: Union[_Qoala_Base_Type, float],
            other_array: Optional[QoalaArray[float]] = None
    ):
        # Nothing to do here
        pass
