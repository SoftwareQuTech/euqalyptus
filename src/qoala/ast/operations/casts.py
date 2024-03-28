from dataclasses import dataclass

from qnet.dialects import arith
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast.operations import QoalaOperation, QoalaExpression
from qoala.ast.value import QoalaFloat, QoalaInteger
from qoala.utils.binding_types import f32, i32


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

    def to_ir(self, ctx: Context):
        self.ir = arith.uitofp(f32(), self.operand.ir)
        return self.ir


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

    def to_ir(self, ctx: Context):
        self.ir = arith.fptoui(i32(), self.operand.ir)
        return self.ir
