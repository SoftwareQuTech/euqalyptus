from dataclasses import dataclass

import qnet.dialects.arith as arith
import qnet.dialects.tensor as tensor
from qnet.ir import Context, Location

from qoala import QoalaProgram
from qoala.ast import checkbaseir
from qoala.ast.operations import QoalaOperation, with_arith_operators
from qoala.ast.value import QoalaExpression, QoalaInteger, QoalaArray
from qoala.errors import OperationNotYetImplementedError
from qoala.utils.binding_types import index
from qoala.utils.debug_info import DebugInfo


@dataclass(init=False)
class CastToIndex(QoalaOperation):
    index_val: QoalaExpression

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        self.index_val: QoalaExpression = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return self.index_val.can_evaluate_to(QoalaInteger)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx
        )
        self.ir_value = arith.index_cast(in_=self.index_val.ir_value, out=index(), loc=source_location)


@dataclass(init=False)
@with_arith_operators
class GetItem(QoalaOperation):
    base_array: QoalaArray
    index: QoalaExpression

    def __init__(self, *operands: QoalaExpression, dbg_info: DebugInfo | None = None,):
        if dbg_info is not None:
            self.debug_info = dbg_info
        super().__init__()
        assert len(operands) == 2
        assert isinstance(operands[0], QoalaArray)
        self.base_array: QoalaArray = operands[0]
        self.index: QoalaExpression = operands[1]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return self.base_array.members_can_evaluate_to(cls)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx
        )
        self.ir_value = tensor.extract(tensor=self.base_array.ir_value, indices=[self.index.ir_value], loc=source_location)


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

    def can_evaluate_to(self, cls) -> bool:
        if self.index.can_evaluate_to(QoalaInteger) and self.base_array.can_evaluate_to(QoalaArray):
            # TODO - We need to make sure that the type of 'base_array' is == cls
            return True
        else:
            return False

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx
        )
        raise OperationNotYetImplementedError(SetItem.__name__)
