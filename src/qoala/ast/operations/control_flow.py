from dataclasses import dataclass
from typing import Optional

import qnet.dialects.qnet as qnet
from qnet.ir import Context, Location

from qoala.ast import checkbaseir, QoalaExpression
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaNumericValue, QoalaBool
from qoala.errors import UnknownTypeError


@dataclass(init=False)
class ReturnResultsOp(QoalaOperation):
    values: list[QoalaExpression]

    def __init__(self, *vals: QoalaExpression | int | float):
        super().__init__()
        self.values = []

        # Users must pass operands as varargs: ReturnResults(x, y).
        for v in vals:
            # IMPORTANT: bool is a subclass of int in Python, so handle it first.
            if isinstance(v, bool):
                self.values.append(
                    QoalaBool.from_immediate(v, dbg_info=self.debug_info)
                )
            elif isinstance(v, (int, float)):
                self.values.append(QoalaNumericValue.from_immediate(v, self.debug_info))
            elif isinstance(v, QoalaExpression):
                self.values.append(v)
            else:
                raise UnknownTypeError(
                    f"Return operation: value '{v}' of type '{type(v)}' is not supported"
                )
        from qoala import QoalaProgram

        # Return should terminate the current block, so append it to the current block now
        # TODO - Actually should terminate the program, can we do something?
        QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return False

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )

        # Compile operands first so ir_value exists
        for v in self.values:
            v.compile(ctx)

        operands = [v.ir_value for v in self.values]

        if len(operands) == 0:
            self.ir_value = qnet.ReturnOp([], loc=source_location)
            return

        self.ir_value = qnet.ReturnOp(operands, loc=source_location)
