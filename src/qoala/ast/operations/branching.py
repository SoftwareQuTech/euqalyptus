from dataclasses import dataclass
from typing import Optional

from qnet.dialects import scf
from qnet.dialects._ods_common import get_op_result_or_op_results
from qnet.ir import Context, Location

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.model import QoalaBlock
from qoala.ast.operations import QoalaOperation


@dataclass(init=False)
class ConditionalBranching(QoalaOperation):
    condition: QoalaExpression
    # Branches need to be a *forward reference* to the place where the code will be
    _branch_true: QoalaBlock
    _branch_false: QoalaBlock

    def __init__(self, condition: QoalaExpression):
        super().__init__()
        self.condition = condition
        QoalaProgram.current_function().append_to_current_block(self)

    def __enter__(self):
        # We create the basic blocks for this conditional branching
        current_function = QoalaProgram.current_function()
        self._branch_true = QoalaBlock(
            current_function.get_new_block_id(), current_function
        )
        self._branch_false = QoalaBlock(
            current_function.get_new_block_id(), current_function
        )
        # And return the true and false branches
        return self._branch_true, self._branch_false

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Exiting the conditional branch context marks the finish of the
        # branching on CFG.
        # We mark the previous block in the nesting sequence as active
        QoalaProgram.current_function().pop_previous_block()

    @property
    def true_dest(self) -> QoalaBlock:
        assert isinstance(self._branch_true, QoalaBlock)
        return self._branch_true

    @true_dest.setter
    def true_dest(self, new_block: QoalaBlock):
        assert isinstance(new_block, QoalaBlock)
        self._branch_true = new_block

    @property
    def false_dest(self) -> QoalaBlock:
        assert isinstance(self._branch_false, QoalaBlock)
        return self._branch_false

    @false_dest.setter
    def false_dest(self, new_block: QoalaBlock):
        assert isinstance(new_block, QoalaBlock)
        self._branch_false = new_block

    def can_evaluate_to(self, cls) -> bool:
        return False

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # Create the scf-IfOp object
        if_op = scf.IfOp(
            self.condition.ir_value,
            (),
            hasElse=len(self._branch_false.operations) >= 1,
            loc=source_location,
        )
        # Compile the then/else block, only if they have operations.
        if len(self._branch_true.operations) >= 1:
            qnet_then_block = if_op.thenRegion.blocks[0]
            self._branch_true.qnet_block = qnet_then_block
            self._branch_true.compile(ctx, location)
        if len(self._branch_false.operations) >= 1:
            qnet_else_block = if_op.elseRegion.blocks[0]
            self._branch_false.qnet_block = qnet_else_block
            self._branch_false.compile(ctx, location)
        # Set the IR value for this conditional branching op
        self._ir_vals = get_op_result_or_op_results(if_op)
