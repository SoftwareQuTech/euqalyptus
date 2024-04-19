from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, TypeVar

from qoala.utils.debug_info import DebugInfo

from qnet.ir import Context, Operation

_T = TypeVar("_T")


@dataclass(init=False)
class QoalaASTElement(ABC):
    debug_info: DebugInfo

    @abstractmethod
    def to_ir(self, ctx: Context):
        pass


@dataclass(init=False)
class QoalaExpression(QoalaASTElement, ABC):
    _ir_vals: List[Operation]

    def __init__(self):
        self._ir_vals = []

    @property
    def ir(self) -> Operation | List[Operation]:
        # We return the "most recent" value for this expression
        return self._ir_vals[-1]

    @ir.setter
    def ir(self, new_hir: Operation) -> None:
        self._ir_vals.append(new_hir)

    @abstractmethod
    def can_evaluate_to(self, cls) -> bool:
        pass
