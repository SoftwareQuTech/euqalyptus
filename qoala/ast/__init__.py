from abc import ABC
from typing import TypeVar

_T = TypeVar("_T")


class QoalaStatement:
    pass


class QoalaExpression:
    pass


class QoalaConstant(QoalaExpression, ABC):
    pass


class QoalaOperation(QoalaExpression, ABC):
    pass
