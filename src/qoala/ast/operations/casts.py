from dataclasses import dataclass

from qnet.dialects import arith
from qnet.extras.types import f32, i32
from qnet.ir import Context, Location

from qoala import QoalaProgram
from qoala.ast import QoalaExpression, checkbaseir
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaFloat, QoalaInteger


@dataclass(init=False)
class IntToFloat(QoalaOperation):
    operand: QoalaExpression

    def __init__(self, *operands):
        super().__init__()
        assert len(operands) == 1
        self.operand = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaFloat

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = arith.uitofp(f32(), self.operand.ir_value, loc=source_location)


@dataclass(init=False)
class FloatToInt(QoalaOperation):
    operand: QoalaExpression

    def __init__(self, *operands):
        super().__init__()
        assert len(operands) == 1
        self.operand = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaInteger

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = arith.fptoui(i32(), self.operand.ir_value, loc=source_location)
