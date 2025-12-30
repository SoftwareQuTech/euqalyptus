from qoala.ast.operations.branching import BranchCode, BranchingOp
from qoala.types.classical.booleans import Bool


class If:
    def __init__(self, condition: Bool | bool):
        # Nothing to do here
        pass

    def __enter__(self):
        # Nothing to do here
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Nothing to do here
        pass


class IfEq(If):
    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs['condition'] = args[0]
        kwargs["branch_code"] = BranchCode.EQUAL
        kwargs["branch_true"] = False
        kwargs["branch_false"] = False
        return BranchingOp(**kwargs)

    def __init__(self, condition: Bool | bool):
        # Nothing to do here - Call to super is to avoid a warning, but it's never called
        super().__init__(condition)


if_eq = IfEq
