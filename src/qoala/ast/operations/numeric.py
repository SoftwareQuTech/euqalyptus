from dataclasses import dataclass

from qoalahir.dialects.arith import AddIOp, AddFOp, SubIOp, SubFOp, MulIOp, MulFOp, DivUIOp, DivFOp
from qoalahir.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression
from qoala.ast.errors import WrongEvaluationTypeError
from qoala.ast.operations import QoalaOperation, with_arith_operators
from qoala.ast.value import QoalaInteger, QoalaFloat


@dataclass(init=False)
@with_arith_operators
class Add(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
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
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self._qoala_hir_val


@dataclass(init=False)
@with_arith_operators
class Subtract(QoalaOperation):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
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
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self._qoala_hir_val


@dataclass(init=False)
@with_arith_operators
class Multiply(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
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
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self._qoala_hir_val


@dataclass(init=False)
@with_arith_operators
class Divide(QoalaExpression):
    operand_a: QoalaExpression
    operand_b: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        self.operand_a = operands[0]
        self.operand_b = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if self.operand_a.can_evaluate_to(cls) and self.operand_b.can_evaluate_to(cls):
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
            raise WrongEvaluationTypeError(f"When creating an operation of type '{self.__class__.__name__}', "
                                           f"the operands cannot be evaluated to any valid value.")
        return self._qoala_hir_val


class ArithOperatorFactory:
    def __new__(cls, *operands, operation: str) -> QoalaExpression:
        if operation in ["__add__", "__radd__", "__iadd__"]:
            return Add(*operands)
        elif operation in ["__sub__", "__rsub__", "__isub__"]:
            return Subtract(*operands)
        elif operation in ["__mul__", "__rmul__", "__imul__"]:
            return Multiply(*operands)
        elif operation in ["__truediv__", "__rtruediv_", "__itruediv__"]:
            return Divide(*operands)
