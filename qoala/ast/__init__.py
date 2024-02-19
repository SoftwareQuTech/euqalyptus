from typing import TypeVar

_T = TypeVar("_T")


class QoalaASTElement:
    pass


class QoalaStatement(QoalaASTElement):
    pass


class QoalaExpression(QoalaASTElement):
    pass


class QoalaOperation(QoalaExpression):
    pass
