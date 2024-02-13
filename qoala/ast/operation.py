from abc import ABC
from enum import Enum, auto


class _OperationType(Enum):
    NullOp = auto()


class Operation(ABC):
    type: _OperationType = _OperationType.NullOp
