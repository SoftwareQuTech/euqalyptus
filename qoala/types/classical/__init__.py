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
        _Internal_Value_Type:
            A value that represents the stored value. The type of the returned
            value will depend on how the value is implemented internally.
        """
        ...
