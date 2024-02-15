from abc import ABC, abstractmethod
from typing import List, Any


class QoalaProgram(ABC):
    """
    Base class for Qoala programs. Any quantum internet program must
    be defined in a class that uses `QoalaProgram` as the base class.
    Programs that extend this class must implement the `main` method,
    which acts as the entry point of the program.
    """

    @abstractmethod
    def main(self, args: List[Any]) -> int:
        """
        Entry point function for a quantum internet program.
        This function must use the quantum and classical primitives
        available in the `qoala` packages and its subpackages.


        Parameters
        ----------
        args : List[Any]
            A list of objects used as the arguments of the function.

        Returns
        -------
        int :
            An integer value, meaningful for the qoala runtime platform.
            Please check the documentation of the qoala platform to match
            the expected return value of a quantum internet program.

        """
        ...
