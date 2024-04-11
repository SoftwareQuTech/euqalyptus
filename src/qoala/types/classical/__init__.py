from abc import ABC
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
    pass
