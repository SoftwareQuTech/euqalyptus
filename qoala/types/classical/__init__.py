from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from qoala.types import QoalaType

_Internal_Value_Type = TypeVar('_Internal_Value_Type')


class QoalaClassicalType(Generic[_Internal_Value_Type], QoalaType, ABC):
    """
    Base class that represents an integer in the classical computation
    model. Similarly, an instance of this class represents a classical
    value of the given type.
    Each subtype of this class can define the operations that can be
    applied to the type. In this sense, and to keep the type closed,
    any operation applied on 1 or more instances (values) of this class
    (type) `will yield a new instance` (value) of the same type.
    """
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
