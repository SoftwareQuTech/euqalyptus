from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

from qoalahir.ir import Context, Operation

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
    _qoala_hir_val: Operation

    @abstractmethod
    def can_evaluate_to(self, cls):
        pass
