from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from qnet.ir import Context, Location
from qnet.dialects.arith import CmpIPredicate

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.operations import QoalaOperation
from qoala.ast.model import BlockPlaceholder


class BranchCode(IntEnum):
    # This enum was created following the comparison values from MLIR arith.cmpi documentation:
    # https://mlir.llvm.org/docs/Dialects/ArithOps/#arithcmpi-arithcmpiop
    EQUAL = CmpIPredicate.eq
    NOT_EQUAL = CmpIPredicate.ne
    SIGNED_LESS_THAN = CmpIPredicate.slt
    SIGNED_LESS_THAN_OR_EQUAL = CmpIPredicate.sle
    SIGNED_GREATER_THAN = CmpIPredicate.sgt
    SIGNED_GREATER_THAN_OR_EQUAL = CmpIPredicate.sge
    UNSIGNED_LESS_THAN = CmpIPredicate.ult
    UNSIGNED_LESS_THAN_OR_EQUAL = CmpIPredicate.ule
    UNSIGNED_GREATER_THAN = CmpIPredicate.ugt
    UNSIGNED_GREATER_THAN_OR_EQUAL = CmpIPredicate.uge


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
