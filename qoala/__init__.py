from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List, Any, Self

from qoala.ast import QoalaASTElement


class QoalaContext:
    def __init__(self):
        self._body: List[QoalaASTElement] = []

    def clear_body(self):
        self._body.clear()

    def add_element_to_body(self, elem: QoalaASTElement):
        self._body.append(elem)


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
    _instance: Self

    def __init__(self, entry_fun: Callable):
        self._context = QoalaContext()
        self._entry_fun = entry_fun
        QoalaProgram._instance = self

    @property
    def _body(self):
        return self._context._body

    @classmethod
    def add_to_body(cls, item: QoalaASTElement):
        QoalaProgram._instance._context.add_element_to_body(item)

    def __call__(self, *args, **kwargs) -> int:
        return self.compile(*args, **kwargs)

    def compile(self, *args, **kwargs):
        # TODO - Implement (if needed) more functionality than just invoking the function
        QoalaProgram._instance = self
        self._context.clear_body()
        return self._entry_fun(*args, **kwargs)
