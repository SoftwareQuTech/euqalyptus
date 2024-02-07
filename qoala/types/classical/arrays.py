from typing import Generic, TypeVar, Self, Optional, Sized

from qoala.types.classical import QoalaClassicalType
from qoala.types.classical.floats import Double
from qoala.types.classical.integer import Int

_Array_Type = TypeVar("_Array_Type", bound=QoalaClassicalType)


class Array(Generic[_Array_Type], Sized):
    internal_representation: list[_Array_Type]

    def __init__(self, *elements: _Array_Type, other_array: Optional[Self] = None):
        self.internal_representation = []
        for element in elements:
            self.internal_representation.append(element)

    def store(self, new_element) -> None:
        self.internal_representation.append(new_element)

    def __repr__(self) -> str:
        return repr(self.internal_representation)

    def __len__(self) -> int:
        """
        Returns the size of this array.
        NOTE: This method returns a `python integer`, which is `not useful
        in a qoala program`. This is due to a technical limitation in the
        python language
        Returns
        -------
        int:
            The size of the stored array
        """
        return len(self.internal_representation)

    def __getitem__(self, item) -> _Array_Type:
        return self.internal_representation[item]

    # Arrays are fixed-length by default (unless you use `store`)
    # so there is no __setitem__ overload


IntArray = Array[Int]
FloatArray = Array[Double]
