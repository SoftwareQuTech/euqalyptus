from abc import ABC
from typing import Type, TypeVar

from qoala.ast import QoalaExpression

_cls = TypeVar("_cls", bound=QoalaExpression)


class QoalaOperation(QoalaExpression, ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _create_expression_for_op(
            op_class: Type[_cls],
            *operands: QoalaExpression,
            **kw_operands: QoalaExpression
    ) -> _cls:
        assert all(isinstance(operand, QoalaExpression) for operand in operands)
        assert all(isinstance(kw_operands[kw_operand], QoalaExpression) for kw_operand in kw_operands)
        return op_class(*operands, **kw_operands)


# Decorator reused from NetQASM repo
def with_arith_operators(cls):
    """A decorator for `QoalaExpression` classes which makes it behave like an arithmetic value.
    """

    def operator_wrapper(method_name):
        """Return a new method for the class given a method name"""

        def operator_implementation(self, *args, **kwargs):
            """Check if the value is set, otherwise raise an error"""
            other: QoalaExpression
            if not isinstance(args[0], QoalaExpression):
                from qoala.ast.value import QoalaNumericValue
                other = QoalaNumericValue.from_immediate(args[0])
            else:
                other = args[0]
            from qoala.ast.operations.numeric import ArithOperatorFactory
            return ArithOperatorFactory(self, other, operation=method_name)

        return operator_implementation

    dunder_methods = [
        "__abs__",
        "__add__",
        "__and__",
        "__bool__",
        "__ceil__",
        "__divmod__",
        "__eq__",
        "__float__",
        "__floor__",
        "__floordiv__",
        "__ge__",
        "__gt__",
        "__hash__",
        "__int__",
        "__invert__",
        "__iadd__",
        "__imul__",
        "__isub__",
        "__itruediv__",
        "__le__",
        "__lshift__",
        "__lt__",
        "__mod__",
        "__mul__",
        "__ne__",
        "__neg__",
        "__or__",
        "__pos__",
        "__pow__",
        "__radd__",
        "__rand__",
        "__rdivmod__",
        "__rfloordiv__",
        "__rlshift__",
        "__rmod__",
        "__rmul__",
        "__ror__",
        "__round__",
        "__rpow__",
        "__rrshift__",
        "__rshift__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__sub__",
        "__truediv__",
        "__xor__",
        "bit_length",
        "conjugate",
        "denominator",
        "imag",
        "numerator",
        "real",
        "to_bytes"
    ]
    for dunder_method in dunder_methods:
        setattr(cls, dunder_method, operator_wrapper(dunder_method))
    return cls
