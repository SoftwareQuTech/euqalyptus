from typing import Generic, TypeVar, Optional, Sized, Union

from qoala.ast.value import QoalaArray, QoalaExpression
from qoala.types.classical import ClassicalType
from qoala.types.classical.floats import Double
from qoala.types.classical.integer import Int

_Array_Type = TypeVar("_Array_Type", bound=ClassicalType)


class _Array(Generic[_Array_Type], Sized):
    def __new__(cls, *elements, **kwargs):
        return QoalaArray(*elements, **kwargs)

    @staticmethod
    def _assert_elements(*elements: QoalaExpression):
        for element in elements:
            # Here we can assert that the elements are expressions
            # whether they can evaluate to a Double or not, is a semantic check
            assert isinstance(element, float) or isinstance(element, QoalaExpression)

    def store(self, new_element: _Array_Type) -> None:
        # Nothing to do here
        pass

    def __repr__(self) -> str:
        pass

    def __len__(self) -> int:
        pass

    def __getitem__(self, item) -> _Array_Type:
        pass

    # Arrays are fixed-length by default (unless you use `store`)
    # so there is no __setitem__ overload


class IntArray(_Array[Int]):
    def __new__(cls, *elements, **kwargs):
        kwargs["base_type"] = int
        kwargs["base_size"] = 32
        if "length" not in kwargs:
            kwargs["length"] = 0
        _Array._assert_elements(*elements)
        return super().__new__(cls, *elements, **kwargs)

    def __init__(
            self,
            *elements: Union[_Array_Type, int],
            other_array: Optional[QoalaArray] = None
    ):
        # Nothing to do here
        pass


class FloatArray(_Array[Double]):
    def __new__(cls, *elements, **kwargs):
        kwargs["base_type"] = float
        kwargs["base_size"] = 32
        if "length" not in kwargs:
            kwargs["length"] = 0
        _Array._assert_elements(*elements)
        return super().__new__(cls, *elements, **kwargs)

    def __init__(
            self,
            *elements: Union[_Array_Type, float],
            other_array: Optional[QoalaArray] = None
    ):
        # Nothing to do here
        pass
