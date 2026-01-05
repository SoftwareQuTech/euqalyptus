from dataclasses import dataclass
from typing import Optional

from qnet.ir import Context, Location
from qnet.dialects import cf

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.model import BranchingBlockPlaceholder, QoalaBlock


@dataclass(init=False)
class UnconditionalBranching(QoalaOperation):
    _destination: QoalaBlock

    def __init__(self, destination: QoalaBlock):
        super().__init__()
        self._destination = destination

    @property
    def destination(self) -> QoalaBlock:
        return self._destination

    def can_evaluate_to(self, cls) -> bool:
        return False

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # TODO - Correctly set the destinations (and the arguments of those blocks)
        self.ir_value = cf.br(dest_operands=(), dest=None, loc=source_location)


@dataclass(init=False)
class ConditionalBranching(QoalaOperation):
    condition: QoalaExpression
    # Branches need to be a *forward reference* to the place where the code will be
    _branch_true: QoalaBlock | BranchingBlockPlaceholder
    _branch_false: QoalaBlock | BranchingBlockPlaceholder
    # Block that joins the CFG back
    _join_block: QoalaBlock

    def __init__(self, condition: QoalaExpression):
        super().__init__()
        self.condition = condition
        QoalaProgram.current_function().append_to_current_block(self)

    def __enter__(self):
        # We create the basic blocks for this conditional branching
        current_function = QoalaProgram.current_function()
        new_block_id = len(current_function.blocks)
        self._join_block = QoalaBlock(new_block_id + 2, current_function)
        self._branch_true = BranchingBlockPlaceholder(
            new_block_id, self, self._join_block, current_function
        )
        self._branch_false = BranchingBlockPlaceholder(
            new_block_id + 1, self, self._join_block, current_function
        )
        # We eagerly emplace the blocks in the function. When using the
        # context of each block, we will mark it correspondingly as active
        current_function.emplace_block(self._branch_true)
        current_function.emplace_block(self._branch_false)
        current_function.emplace_block(self._join_block)
        # And return the true and false branches
        return self._branch_true, self._branch_false

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Exiting the conditional branch context marks the finish of the
        # branching on CFG. We mark the join block as active
        QoalaProgram.current_function().mark_as_current_block(self._join_block)

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

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.condition.compile(ctx, location)
        # TODO - Correctly set the destinations (and the arguments of those blocks)
        self.ir_value = cf.cond_br(
            condition=self.condition.ir_value,
            true_dest_operands=(),
            false_dest_operands=(),
            true_dest=None,
            false_dest=None,
            loc=source_location,
        )

    def can_evaluate_to(self, cls) -> bool:
        return False
