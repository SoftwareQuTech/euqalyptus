from typing import List

from qoala.ast import QoalaExpression
from qoala.ast.operations.control_flow import ReturnResultsOp


class ReturnResults:
    """
    User-facing SDK helper to emit qnet.return (0..N operands).

    Usage:
        ReturnResults()                    # qnet.return
        ReturnResults(x)                   # qnet.return %x
        ReturnResults(x, y, z)             # qnet.return %x, %y, %z

    Alias provided at bottom: return_results = ReturnResults
    """

    def __new__(cls, *args: QoalaExpression | int | float | list | tuple):
        processed_args: List[QoalaExpression | int | float] = []
        # Flatten all the args
        for arg in args:
            if isinstance(arg, (list, tuple)):
                processed_args.extend(arg)
            else:
                processed_args.append(arg)
        return ReturnResultsOp(*processed_args)

    def __init__(self, *args, **kwargs):
        pass


return_results = ReturnResults
