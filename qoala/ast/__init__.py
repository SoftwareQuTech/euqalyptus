from typing import TypeVar, Type

from qoala.ast.value import QoalaInteger, QoalaFloat

_T = TypeVar("_T")


class QoalaASTElement:
    pass


class QoalaStatement(QoalaASTElement):
    pass


class QoalaExpression(QoalaASTElement):
    pass


_cls = TypeVar("_cls", bound=QoalaExpression)


class QoalaOperation(QoalaExpression):
    @staticmethod
    def _create_expression_for_op(op_class: Type[_cls], *operands: QoalaExpression) -> _cls:
        assert all(isinstance(operand, QoalaExpression) for operand in operands)
        return op_class(*operands)


FloatOrExpression = QoalaFloat | QoalaExpression | float
IntegerOrExpression = QoalaInteger | QoalaExpression | int
