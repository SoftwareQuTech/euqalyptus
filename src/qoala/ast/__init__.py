from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Type

from qoalahir.ir import Context, Operation

_T = TypeVar("_T")


@dataclass(init=False)
class QoalaASTElement(ABC):

    @abstractmethod
    def to_hir(self, ctx: Context):
        pass


class QoalaStatement(QoalaASTElement):
    pass


@dataclass(init=False)
class QoalaExpression(QoalaASTElement, ABC):
    _qoala_hir_val: Operation

    @abstractmethod
    def can_evaluate_to(self, cls):
        pass


_cls = TypeVar("_cls", bound=QoalaExpression)


class QoalaOperation(QoalaExpression):
    @staticmethod
    def _create_expression_for_op(
            op_class: Type[_cls],
            *operands: QoalaExpression,
            **kw_operands: QoalaExpression
    ) -> _cls:
        assert all(isinstance(operand, QoalaExpression) for operand in operands)
        assert all(isinstance(kw_operands[kw_operand], QoalaExpression) for kw_operand in kw_operands)
        return op_class(*operands, **kw_operands)
