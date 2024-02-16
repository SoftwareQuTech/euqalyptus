from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List, Any


class QoalaProgramBase(ABC):
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


class QoalaProgram:
    """
    Function decorator used to mark methods as qoala programs.
    TODO - Complete this doc
    """

    _entry_fun: Callable[[Any, ...], int]
    _body: List

    def __init__(self, entry_fun: Callable):
        self._entry_fun = entry_fun
        self._body = []

    def __call__(self, *args, **kwargs) -> int:
        return self._entry_fun(*args, **kwargs)

    def compile(self, *args, **kwargs):
        # TODO - Implement (if needed) more functionality than just invoking the function
        return self.__call__(*args, **kwargs)
