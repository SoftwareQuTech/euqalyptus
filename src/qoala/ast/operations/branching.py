from dataclasses import dataclass
from typing import Optional

from qnet.ir import Context, Location
from qnet.dialects import cf

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.model import BlockPlaceholder


@dataclass(init=False)
class ConditionalBranching(QoalaOperation):
    condition: QoalaExpression
    # Branches need to be a *forward reference* to the place where the code will be
    _branch_true: BlockPlaceholder
    _branch_false: BlockPlaceholder

    def __init__(self, condition: QoalaExpression):
        super().__init__()
        self.condition = condition
        QoalaProgram.current_function().append_to_current_block(self)

    def __enter__(self):
        self._branch_true = BlockPlaceholder()
        self._branch_false = BlockPlaceholder()
        return self._branch_true, self._branch_false

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Exiting the conditional branch context marks the finish of the
        # branching on CFG. We insert a new empty block (the join block)
        # in the current function.
        QoalaProgram.current_function().emplace_new_empty_block()

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        pass

    def can_evaluate_to(self, cls) -> bool:
        return False
