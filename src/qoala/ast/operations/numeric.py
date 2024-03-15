from dataclasses import dataclass

from qoala import QoalaProgram
from qoala.ast import QoalaOperation
from qoala.ast.value import QoalaExpression, QoalaInteger, QoalaFloat
#from qoala.utils import with_arith_operators

from qoalahir.ir import Context
from qoalahir.dialects.arith import AddIOp, AddFOp, SubIOp, SubFOp, MulIOp, MulFOp, DivUIOp, DivSIOp, DivFOp


@dataclass(init=False)
class Add(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if isinstance(self.operand_a, cls) and isinstance(self.operand_b, cls):
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self._qoala_hir_val = AddIOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self._qoala_hir_val = AddFOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        else:
            raise RuntimeError()
        return self._qoala_hir_val


@dataclass(init=False)
class Subtract(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if isinstance(self.operand_a, cls) and isinstance(self.operand_b, cls):
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self._qoala_hir_val = SubIOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self._qoala_hir_val = SubFOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        else:
            raise RuntimeError()
        return self._qoala_hir_val


@dataclass(init=False)
class Multiply(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if isinstance(self.operand_a, cls) and isinstance(self.operand_b, cls):
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self._qoala_hir_val = MulIOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self._qoala_hir_val = MulFOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        else:
            raise RuntimeError()
        return self._qoala_hir_val


@dataclass(init=False)
class Divide(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if isinstance(self.operand_a, cls) and isinstance(self.operand_b, cls):
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - In the meantime we assume both operands are of the same type
        #        In the future we could implement semantic checks to automatically cast one
        #        type to another one
        if self.operand_a.can_evaluate_to(QoalaInteger):
            self._qoala_hir_val = DivUIOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        elif self.operand_a.can_evaluate_to(QoalaFloat):
            self._qoala_hir_val = DivFOp(self.operand_a._qoala_hir_val, self.operand_b._qoala_hir_val)
        else:
            raise RuntimeError()
        return self._qoala_hir_val
