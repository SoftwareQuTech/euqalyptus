from dataclasses import dataclass

import qoalahir.dialects.arith as arith
from qoalahir.ir import Context

from qoala import QoalaProgram
from qoala.ast.errors import OperationNotYetImplementedError
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaExpression, QoalaInteger, QoalaArray
from qoala.utils.binding_types import index


@dataclass(init=False)
class CastToIndex(QoalaExpression):
    index_val: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        self.index_val: QoalaExpression = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.index_val.can_evaluate_to(QoalaInteger):
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        self.hir = arith.index_cast(in_=self.index_val.hir, out=index())
        return self.hir


@dataclass(init=False)
class GetItem(QoalaOperation):
    base_array: QoalaArray
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        assert isinstance(operands[0], QoalaArray)
        self.base_array: QoalaArray = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.index.can_evaluate_to(QoalaInteger) and self.base_array.can_evaluate_to(QoalaArray):
            # TODO - We need to make sure that the base type of 'base_array' is cls
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - Implement the HIR representation fo arrays - tensor or vector?
        self.hir = tensor.extract(tensor=self.base_array.hir, indices=[self.index.hir])
        return self.hir


@dataclass(init=False)
class SetItem(QoalaOperation):
    base_array: QoalaArray
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 2
        assert isinstance(operands[0], QoalaArray)
        self.base_array: QoalaArray = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.index.can_evaluate_to(QoalaInteger) and self.base_array.can_evaluate_to(QoalaArray):
            # TODO - We need to make sure that the type of 'base_array' is == cls
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        raise OperationNotYetImplementedError(SetItem.__name__)
