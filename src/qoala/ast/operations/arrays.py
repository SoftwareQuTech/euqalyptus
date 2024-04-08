from dataclasses import dataclass

import qnet.dialects.arith as arith
import qnet.dialects.tensor as tensor
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast.errors import OperationNotYetImplementedError
from qoala.ast.operations import QoalaOperation, with_arith_operators
from qoala.ast.qubit import QoalaQubit, QoalaMultiEprs, QoalaSingleEprs
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

    def to_ir(self, ctx: Context):
        self.ir = arith.index_cast(in_=self.index_val.ir, out=index())
        return self.ir


@dataclass(init=False)
@with_arith_operators
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
        return self.base_array.members_can_evaluate_to(cls)

    def to_ir(self, ctx: Context):
        self.ir = tensor.extract(tensor=self.base_array.ir, indices=[self.index.ir])
        return self.ir


@dataclass(init=False)
class GetQItem(QoalaSingleEprs):
    eprs_set: QoalaMultiEprs
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 2
        assert isinstance(operands[0], QoalaMultiEprs)
        self.eprs_set: QoalaMultiEprs = operands[0]
        self.index: QoalaExpression = operands[1]
        # This operation does not need to be added to the body of the program, since
        # it is only useful for the internals of the frontend to identify the
        # specific remote qubit on the
        super().__init__(self.eprs_set.remote_name, declare_remote=False)

    def can_evaluate_to(self, cls):
        return cls == QoalaQubit

    def to_ir(self, ctx: Context):
        self.ir = tensor.extract(tensor=self.eprs_set.ir, indices=[self.index.ir])
        return self.ir


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

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(SetItem.__name__)
