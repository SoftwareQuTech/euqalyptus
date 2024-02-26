from typing import TypeVar, Type

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
    def _create_expression_for_op(
            op_class: Type[_cls],
            *operands: QoalaExpression,
            **kw_operands: QoalaExpression
    ) -> _cls:
        assert all(isinstance(operand, QoalaExpression) for operand in operands)
        assert all(isinstance(kw_operands[kw_operand], QoalaExpression) for kw_operand in kw_operands)
        return op_class(*operands, **kw_operands)
