from abc import ABC

from euqalyptus.types import QoalaType


class QoalaQuantumType(QoalaType, ABC):
    """
    Base class for qoala quantum types
    """

    pass


from .qubit import LocalQubit, Entangle, ScopedQubit
