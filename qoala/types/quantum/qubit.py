from abc import ABC, abstractmethod
from typing import Optional, Self, Union

from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Measure, IntegerType
from qoala.types.quantum import QoalaQuantumType


class Qubit(QoalaQuantumType, ABC):
    """
    Class representing a qubit in the hybrid program.

    A `Qubit` instance represents a quantum state that is stored in a physical qubit
    somewhere in the quantum node.
    The particular qubit is identified by its virtual qubit ID.
    To which physical qubit ID this is mapped (at a given time), is handled completely
    by the quantum node controller and is not known to the `Qubit` itself.

    A `Qubit` object can be instantiated in a program.
    Such an instantiation is automatically compiled into NetQASM instructions that
    allocate and initialize a new qubit in the quantum node controller.

    A `Qubit` object may also be obtained by other SDK functions that return them, like
    the `create()` method on an `EPRSocket`, which returns the object as a handle to
    the qubit that is now entangled with one in another node.

    Qubit operations like applying gates and measuring them are done by calling
    methods on a `Qubit` instance.
    """

    @abstractmethod
    def measure(self) -> Measure:
        """
        Measure the qubit in the standard basis and get the measurement outcome.

        Returns
        -------
            The value of the measure, as a `Measure` object
        """
        ...

    @abstractmethod
    def X(self):
        """
        Applies an X gate on the qubit.

        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def Y(self):
        """
        Applies an Y gate on the qubit.
        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def Z(self):
        """
        Applies a Z gate on the qubit.
        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def T(self):
        """
        Applies a T gate on the qubit.
        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def H(self):
        """
        Applies a Hadamard gate on the qubit.
        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def K(self):
        """
        Applies a K gate on the qubit.
        A K gate moves the |0> state to +|i> (positive Y) and vice versa.
        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def S(self):
        """
        Applies an S gate on the qubit.
        An S gate is a Z-rotation with angle pi/2.
        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def rot_X(
            self,
            n: Union[int, IntegerType] = 0,
            d: Union[int, IntegerType] = 0,
            angle: Union[float, Float, None] = None
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

    @abstractmethod
    def rot_Y(
            self,
            n: Union[int, IntegerType] = 0,
            d: Union[int, IntegerType] = 0,
            angle: Union[float, Float, None] = None
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

    @abstractmethod
    def rot_Z(
            self,
            n: Union[int, IntegerType] = 0,
            d: Union[int, IntegerType] = 0,
            angle: Union[float, Float, None] = None
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def reset(self) -> None:
        r"""
        Reset the qubit to the state \|0>.

        Returns
        -------
        None
        """
        ...

    @abstractmethod
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
    def measure(self) -> Measure:
        # TODO - Implement: Modify the dummy object returned
        return Measure()

    def X(self):
        # TODO - Implement
        pass

    def Y(self):
        # TODO - Implement
        pass

    def Z(self):
        # TODO - Implement
        pass

    def T(self):
        # TODO - Implement
        pass

    def H(self):
        # TODO - Implement
        pass

    def K(self):
        # TODO - Implement
        pass

    def S(self):
        # TODO - Implement
        pass

    def rot_X(
            self,
            n: Union[int, IntegerType] = 0,
            d: Union[int, IntegerType] = 0,
            angle: Union[float, Float, None] = None
    ):
        # TODO - Implement
        pass

    def rot_Y(
            self,
            n: Union[int, IntegerType] = 0,
            d: Union[int, IntegerType] = 0,
            angle: Union[float, Float, None] = None
    ):
        # TODO - Implement
        pass

    def rot_Z(
            self,
            n: Union[int, IntegerType] = 0,
            d: Union[int, IntegerType] = 0,
            angle: Union[float, Float, None] = None
    ):
        # TODO - Implement
        pass

    def cnot(self, target: Self) -> None:
        # TODO - Implement
        pass

    def cphase(self, target: Self) -> None:
        # TODO - Implement
        pass

    def reset(self) -> None:
        # TODO - Implement
        pass

    def free(self) -> None:
        # TODO - Implement
        pass
