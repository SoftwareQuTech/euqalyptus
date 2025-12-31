from qoala.ast.operations.branching import BranchCode, BranchingOp
from qoala.types.classical.booleans import Bool
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.integer import QoalaIntegerType


class IfCondition:
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.EQUAL
        return BranchingOp(**kwargs)

    def __init__(self, condition: Bool | bool):
        # Nothing to do here
        pass

    def __enter__(self):
        # Nothing to do here
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Nothing to do here
        pass


class IfEq(IfCondition):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.EQUAL
        return BranchingOp(**kwargs)

    def __init__(self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfNeq(IfCondition):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.NOT_EQUAL
        return BranchingOp(**kwargs)

    def __init__(self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfLt(IfCondition):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.SIGNED_LESS_THAN
        return BranchingOp(**kwargs)

    def __init__(self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfLe(IfCondition):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.SIGNED_LESS_THAN_OR_EQUAL
        return BranchingOp(**kwargs)

    def __init__(self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfGt(IfCondition):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.SIGNED_GREATER_THAN
        return BranchingOp(**kwargs)

    def __init__(self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


class IfGe(IfCondition):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["condition"] = args[0]
        kwargs["branch_code"] = BranchCode.SIGNED_GREATER_THAN_OR_EQUAL
        return BranchingOp(**kwargs)

    def __init__(self, *operands: QoalaIntegerType | QoalaFloatingPointType | int | float):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(*operands)


if_cond = IfCondition
if_eq = IfEq
if_neq = IfNeq
if_lt = IfLt
if_le = IfLe
if_ge = IfGe
if_gt = IfGt
