from dataclasses import dataclass

from qoala import QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaExpression, QoalaInteger, QoalaArray

from qoalahir.ir import Context


@dataclass(init=False)
class GetItem(QoalaOperation):
    base_array: QoalaExpression
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.base_array: QoalaExpression = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.index.can_evaluate_to(QoalaInteger) and self.base_array.can_evaluate_to(QoalaArray):
            # TODO - We need to make sure that the type of 'base_array' is == cls
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - Implement the HIR representation fo arrays - tensor or vector?
        self._qoala_hir_val = None
        return self._qoala_hir_val


@dataclass(init=False)
class SetItem(QoalaOperation):
    base_array: QoalaExpression
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.base_array: QoalaExpression = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.index.can_evaluate_to(QoalaInteger) and self.base_array.can_evaluate_to(QoalaArray):
            # TODO - We need to make sure that the type of 'base_array' is == cls
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - Implement the HIR representation fo arrays - tensor or vector?
        self._qoala_hir_val = None
        return self._qoala_hir_val
