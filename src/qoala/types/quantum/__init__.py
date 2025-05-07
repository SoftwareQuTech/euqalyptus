from abc import ABC

from qoala.types import QoalaType


class QoalaQuantumType(QoalaType, ABC):
    """
    Base class for qoala quantum types
    """
    pass


from .qubit import LocalQubit, Entangle