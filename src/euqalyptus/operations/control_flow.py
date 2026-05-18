from typing import List

from euqalyptus.ast import QoalaExpression
from euqalyptus.ast.operations.control_flow import ReturnResultsOp


class ReturnResults:
    """Record a ``qnet.return`` op that terminates the current function.

    Use ``return_results(...)`` (the lowercase alias) inside a
    ``@QoalaProgram`` body to return classical values — typically
    measurement outcomes — from the program. If the function body
    finishes without an explicit ``return_results(...)`` call, the SDK
    inserts an empty ``qnet.return`` automatically; you only need to
    call this explicitly when you want to return one or more values or
    to terminate early.

    Examples:
        ``ReturnResults()`` → records ``qnet.return``.

        ``ReturnResults(x)`` → records ``qnet.return %x``.

        ``ReturnResults(x, y, z)`` → records ``qnet.return %x, %y, %z``.

        ``ReturnResults([x, y, z])`` → same as the variadic form;
        ``list`` / ``tuple`` operands are flattened.

    Args:
        *args: Zero or more values to return. Each value must be a
            :class:`QoalaExpression` (the recorded form of an SDK
            value), a Python ``int`` or ``float`` literal (auto-
            promoted), or a ``list``/``tuple`` of the same — those are
            flattened in place.

    Returns:
        A :class:`ReturnResultsOp` AST node representing the return.
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
"""Lowercase alias of :class:`ReturnResults`. Records ``qnet.return``."""
