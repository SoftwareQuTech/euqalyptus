from qoala.ast.operations.control_flow import ReturnResultsOp
from qoala.ast import QoalaExpression

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
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return ReturnResultsOp(*args[0])
        return ReturnResultsOp(*args)

    def __init__(self, *args, **kwargs):
        pass

return_results = ReturnResults
