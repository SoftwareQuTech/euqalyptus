from abc import ABC
from enum import Enum
from typing import Type, TypeVar

from euqalyptus.ast import QoalaExpression
from euqalyptus.utils.debug_info import get_debug_info

_cls = TypeVar("_cls", bound=QoalaExpression)


class QoalaOperation(QoalaExpression, ABC):

    def __init__(self):
        if not hasattr(self, "debug_info"):
            self.debug_info = get_debug_info()
        super().__init__()

    @staticmethod
    def create_expression_for_op(
        op_class: Type[_cls], *operands: QoalaExpression, **kw_operands: QoalaExpression
    ) -> _cls:
        assert all(isinstance(operand, QoalaExpression) for operand in operands)
        assert all(
            isinstance(kw_operands[kw_operand], QoalaExpression)
            for kw_operand in kw_operands
        )
        return op_class(*operands, **kw_operands)


class _MethodType(Enum):
    ARITHMETIC = 1
    BITWISE = 2
    ORDER = 3


# Decorator adapted from NetQASM repo
def with_operators(arith: bool = True, bitwise: bool = False, order: bool = False):
    """A decorator for `QoalaExpression` classes which add support for common operators."""

    def _inner_decorator(cls):
        def operator_wrapper(method_type: _MethodType, method_name: str):
            """Return a new method for the class given a method name"""

            def operator_implementation(self, *args, **kwargs):
                from euqalyptus.ast.operations.bitwise import BitwiseOperatorFactory
                from euqalyptus.ast.operations.numeric import ArithOperatorFactory
                from euqalyptus.ast.operations.order import OrderOperatorFactory

                if len(args) >= 1:
                    # Binary operation, We use the first arg as the second operand.
                    # Any other extra operands will simply be ignored
                    other: QoalaExpression
                    if not isinstance(args[0], QoalaExpression):
                        from euqalyptus.ast.value import QoalaNumericValue

                        other = QoalaNumericValue.from_immediate(
                            args[0], self.debug_info
                        )
                    else:
                        other = args[0]

                    match method_type:
                        case _MethodType.ARITHMETIC:
                            return ArithOperatorFactory(
                                self, other, operation=method_name
                            )
                        case _MethodType.BITWISE:
                            return BitwiseOperatorFactory(
                                self, other, operation=method_name
                            )
                        case _MethodType.ORDER:
                            return OrderOperatorFactory(
                                self, other, operation=method_name
                            )
                else:
                    # len(args) == 0 => The operation is unary => There is no "other" operand
                    match method_type:
                        case _MethodType.BITWISE:
                            return BitwiseOperatorFactory(self, operation=method_name)
                        case _MethodType.ORDER:
                            return OrderOperatorFactory(self, operation=method_name)
                        case _:
                            raise RuntimeError(
                                f"No unary operator implementation for class '{method_type}'"
                            )

            return operator_implementation

        arith_dunder_methods = [
            "__abs__",
            "__add__",
            "__ceil__",
            "__divmod__",
            "__float__",
            "__floor__",
            "__floordiv__",
            "__hash__",
            "__int__",
            "__invert__",
            "__iadd__",
            "__imul__",
            "__isub__",
            "__itruediv__",
            "__lshift__",
            "__mod__",
            "__mul__",
            "__pos__",
            "__pow__",
            "__radd__",
            "__rdivmod__",
            "__rfloordiv__",
            "__rlshift__",
            "__rmod__",
            "__rmul__",
            "__round__",
            "__rpow__",
            "__rrshift__",
            "__rshift__",
            "__rsub__",
            "__rtruediv__",
            "__sub__",
            "__truediv__",
            "bit_length",
            "conjugate",
            "denominator",
            "imag",
            "numerator",
            "real",
            "to_bytes",
        ]
        bitwise_dunder_methods = [
            "__and__",
            "__bool__",
            "__ne__",
            "__invert__",
            "__neg__",
            "__or__",
            "__rand__",
            "__ror__",
            "__rxor__",
            "__xor__",
        ]
        order_dunder_methods = [
            "__eq__",
            "__ge__",
            "__gt__",
            "__le__",
            "__lt__",
            "__ne__",
            "bit_length",
            "conjugate",
            "to_bytes",
        ]
        for dunder_method in arith_dunder_methods:
            setattr(
                cls,
                dunder_method,
                operator_wrapper(_MethodType.ARITHMETIC, dunder_method),
            )
        for dunder_method in bitwise_dunder_methods:
            setattr(
                cls, dunder_method, operator_wrapper(_MethodType.BITWISE, dunder_method)
            )
        for dunder_method in order_dunder_methods:
            setattr(
                cls, dunder_method, operator_wrapper(_MethodType.ORDER, dunder_method)
            )
        return cls

    return _inner_decorator
