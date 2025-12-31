from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from qnet.ir import Context, Location
from qnet.dialects.arith import CmpIPredicate

from qoala import QoalaExpression, QoalaProgram
from qoala.ast.operations import QoalaOperation


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
class BranchingOp(QoalaOperation):
    condition: QoalaExpression
    branch_code: BranchCode
    # Branches need to be a *forward reference* to the place where the code will be
    branch_true: bool
    branch_false: bool

    def __init__(
        self,
        condition: QoalaExpression,
        branch_code: BranchCode,
        branch_true: bool,
        branch_false: bool,
    ):
        super().__init__()
        self.condition = condition
        self.branch_code = branch_code
        self.branch_true = branch_true
        self.branch_false = branch_false
        QoalaProgram.add_to_current_function_body(self)

    def __enter__(self):
        # TODO - Implement this
        return self.branch_true, self.branch_false

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO - Implement this
        pass

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        pass

    def can_evaluate_to(self, cls) -> bool:
        return False
