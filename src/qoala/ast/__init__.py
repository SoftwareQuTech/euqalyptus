from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, TypeVar

from qnet.ir import Context, Operation

_T = TypeVar("_T")


@dataclass(init=False)
class QoalaASTElement(ABC):

    @abstractmethod
    def to_hir(self, ctx: Context):
        pass


class QoalaStatement(QoalaASTElement, ABC):
    pass


@dataclass(init=False)
class QoalaExpression(QoalaASTElement, ABC):
    _qoala_hir_vals: List[Operation]

    def __init__(self):
        self._qoala_hir_vals = []

    @property
    def hir(self) -> Operation | List[Operation]:
        # We return the "most recent" value for this expression
        return self._qoala_hir_vals[-1]

    @hir.setter
    def hir(self, new_hir: Operation) -> None:
        self._qoala_hir_vals.append(new_hir)

    @abstractmethod
    def can_evaluate_to(self, cls) -> bool:
        pass
