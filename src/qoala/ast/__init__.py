from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, TypeVar

from qoala.utils.debug_info import DebugInfo

from qnet.ir import Context, Operation

_T = TypeVar("_T")


class checkbaseir:
    def __init__(self, to_ir_func):
        self._to_ir_func = to_ir_func

    def __call__(self, *args, **kwargs):
        if args[0].ir is not None:
            return args[0].ir
        else:
            return self._to_ir_func(*args, **kwargs)

    def __get__(self, instance, owner):
        from functools import partial
        return partial(self.__call__, instance)


@dataclass(init=False)
class QoalaExpression(ABC):
    _ir_vals: List[Operation]
    debug_info: DebugInfo

    @abstractmethod
    def to_ir(self, ctx: Context):
        pass

    def __init__(self):
        self._ir_vals = []

    @property
    def ir(self) -> Operation | List[Operation] | None:
        if len(self._ir_vals) <= 0:
            return None
        # We return the "most recent" value for this expression
        return self._ir_vals[-1]

    @ir.setter
    def ir(self, new_hir: Operation) -> None:
        self._ir_vals.append(new_hir)

    @abstractmethod
    def can_evaluate_to(self, cls) -> bool:
        pass
    #
    # @abstractmethod
    # def value(self) -> Self:
    #     pass
