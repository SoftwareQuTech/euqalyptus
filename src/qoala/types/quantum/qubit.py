from abc import ABC
from typing import Optional, Self

from qoala.ast import QoalaExpression
from qoala.ast.qubit import QoalaLocalQubit, QoalaEprs
from qoala.ast.value import QoalaBit
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.integer import QoalaIntegerType
from qoala.types.quantum import QoalaQuantumType


class Qubit(QoalaQuantumType, ABC):
    """
    Class representing a qubit in the hybrid program.

    A `Qubit` instance represents a quantum state that is stored in a physical qubit
    somewhere in the quantum node.

    A `Qubit` object can be instantiated in a program.
    Such an instantiation is automatically compiled into the QoalaHIR instructions that
    allocate and initialize a new qubit in the quantum node controller.

    Qubit operations like applying gates and measuring them are done by calling
    methods on a `Qubit` instance.
    """

    def measure(self) -> QoalaBit:
        """
        Measure the qubit in the standard basis and get the measurement outcome.

        Returns
        -------
            The value of the measure, as a `Bit` object
        """
        ...

    def X(self):
        """
        Applies an X gate on the qubit.

        Returns
        -------
        None
        """
        ...

    def Y(self):
        """
        Applies an Y gate on the qubit.
        Returns
        -------
        None
        """
        ...

    def Z(self):
        """
        Applies a Z gate on the qubit.
        Returns
        -------
        None
        """
        ...

    def T(self):
        """
        Applies a T gate on the qubit.
        Returns
        -------
        None
        """
        ...

    def H(self):
        """
        Applies a Hadamard gate on the qubit.
        Returns
        -------
        None
        """
        ...

    def K(self):
        """
        Applies a K gate on the qubit.
        A K gate moves the |0> state to +|i> (positive Y) and vice versa.
        Returns
        -------
        None
        """
        ...

    def S(self):
        """
        Applies an S gate on the qubit.
        An S gate is a Z-rotation with angle pi/2.
        Returns
        -------
        None
        """
        ...

    def rot_X(
            self,
            n: int | QoalaIntegerType = 0,
            d: int | QoalaIntegerType = 0,
            angle: float | QoalaFloatingPointType | None = None
    ):
        """
        Do a rotation around the X-axis of the specified angle.

        The angle is interpreted as `n * pi / 2 ^d` radians.
        For example, (n, d) = (1, 2) represents an angle of pi/4 radians.
        If `angle` is specified, `n` and `d` are ignored and this instruction is
        automatically converted into a sequence of (n, d) rotations such that the
        discrete (n, d) values approximate the original angle.

        Parameters
        ----------
        n: int
            numerator of discrete angle specification. Can be a Template,
            in which case the subroutine containing this command should first be
            instantiated before flushing.
        d: int
            denomerator of discrete angle specification
        angle: Optional[float]
            exact floating-point angle, defaults to None

        Returns
        -------
        None
        """
        ...

    def rot_Y(
            self,
            n: int | QoalaIntegerType = 0,
            d: int | QoalaIntegerType = 0,
            angle: float | QoalaFloatingPointType | None = None
    ):
        """
        Do a rotation around the Y-axis of the specified angle.

        The angle is interpreted as `n * pi / 2 ^d` radians.
        For example, (n, d) = (1, 2) represents an angle of pi/4 radians.
        If `angle` is specified, `n` and `d` are ignored and this instruction is
        automatically converted into a sequence of (n, d) rotations such that the
        discrete (n, d) values approximate the original angle.

        Parameters
        ----------
        n: int
            numerator of discrete angle specification. Can be a Template,
            in which case the subroutine containing this command should first be
            instantiated before flushing.
        d: int
            denomerator of discrete angle specification
        angle: Optional[float]
            exact floating-point angle, defaults to None

        Returns
        -------
        None
        """
        ...

    def rot_Z(
            self,
            n: int | QoalaIntegerType = 0,
            d: int | QoalaIntegerType = 0,
            angle: float | QoalaFloatingPointType | None = None
    ):
        """
        Do a rotation around the Z-axis of the specified angle.

        The angle is interpreted as `n * pi / 2 ^d` radians. For example, (n, d)
        = (1, 2) represents an angle of pi/4 radians. If `angle` is specified,
        `n` and `d` are ignored and this instruction is automatically converted
        into a sequence of (n, d) rotations such that the discrete (n, d) values
        approximate the original angle.

        Parameters
        ----------
        n: int
            numerator of discrete angle specification. Can be a Template,
            in which case the subroutine containing this command should first be
            instantiated before flushing.
        d: int
            denomerator of discrete angle specification
        angle: Optional[float]
            exact floating-point angle, defaults to None

        Returns
        -------
        None
        """
        ...

    def cnot(self, target: Self) -> None:
        """
        Apply a CNOT gate between this qubit (control) and a target qubit.

        Parameters
        ----------
        target: Qubit
            target qubit. Should have the same connection as this qubit.

        Returns
        -------
        None
        """
        ...

    def cphase(self, target: Self) -> None:
        """
        Apply a CPHASE (CZ) gate between this qubit (control) and a target qubit.

        Parameters
        ----------
        target: Qubit
            target qubit. Should have the same connection as this qubit.

        Returns
        -------
        None
        """
        ...

    def reset(self) -> None:
        r"""
        Reset the qubit to the state \|0>.

        Returns
        -------
        None
        """
        ...

    def free(self) -> None:
        """
        Free the qubit and its virtual ID.

        After freeing, the underlying physical qubit can be used to store another state.

        Returns
        -------
        None
        """
        ...


class LocalQubit(Qubit):
    """
    Represents a local qubit used for local quantum computation.
    """
    def __new__(cls, *args, **kwargs):
        return QoalaLocalQubit()

    def __init__(self):
        # Nothing to do here
        pass


class Entangle(Qubit):
    """
    Represents a local set of qubits used for quantum entanglement with a remote host.
    """
    def __new__(cls, name: str, n: int | QoalaExpression):
        return QoalaEprs(name, n)

    def __init__(self, name: str, num: int | QoalaExpression):
        # Nothing to do here
        pass

    def __getitem__(self, item: int | QoalaExpression):
        # Nothing to do here
        pass
