from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from qoala.types import QoalaType

_Internal_Value_Type = TypeVar('_Internal_Value_Type')


class QoalaClassicalType(Generic[_Internal_Value_Type], QoalaType, ABC):
    @abstractmethod
    def _get_value(self) -> _Internal_Value_Type:
        """
        Returns the internal representation of this classical type.
        NOTE: This method is intended to be used `for testing purposes only`
        Returns
        -------
        _Int_Val_T:
            A value of the declared type, depending on how the type is
            implemented internally
        """
        ...
