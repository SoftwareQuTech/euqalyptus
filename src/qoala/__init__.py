from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections.abc import Callable
from threading import Lock
from typing import List, Self, Any, Dict

from qoala.ast import QoalaASTElement


class NotYetCompiledError(RuntimeError):
    pass


@dataclass
class QoalaModule:
    _body: List[QoalaASTElement]

    def __init__(self):
        self._body = []

    def clear_body(self):
        self._body.clear()

    def add_element_to_body(self, elem: QoalaASTElement):
        self._body.append(elem)

    @property
    def asm(self) -> str:
        return "TODO"

    def __str__(self) -> str:
        return self.asm


class QoalaProgramBase(ABC):
    """
    Base class for Qoala programs. Any quantum internet program must
    be defined in a class that uses `QoalaProgram` as the base class.
    Programs that extend this class must implement the `main` method,
    which acts as the entry point of the program.
    """

    @abstractmethod
    def main(self, *args: Any, **kwargs: Dict[Any, Any]) -> Any:
        """
        Entry point function for a quantum internet program.
        This function must use the quantum and classical primitives
        available in the `qoala` packages and its subpackages.


        Parameters
        ----------
        args : List[Any]
            A list of objects used as the arguments of the function.

        kwargs : Dict[Any, Any]
            A dictionary containing the keyworded arguments for the function.

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
    _compiler_lock: Lock = Lock()
    _is_compiled: bool

    def __init__(self, entry_fun: Callable):
        self._module = QoalaModule()
        self._entry_fun = entry_fun
        self._is_compiled = False

    @property
    def _body(self):
        return self._module._body

    @property
    def module(self):
        if not self._is_compiled:
            raise NotYetCompiledError("The program has not been compiled yet. Did you invoke 'compile()' on it?")
        else:
            return self._module

    @classmethod
    def add_to_body(cls, item: QoalaASTElement):
        if hasattr(QoalaProgram, "_instance"):
            QoalaProgram._instance._module.add_element_to_body(item)

    def __call__(self, *args, **kwargs) -> QoalaModule:
        return self.compile(*args, **kwargs)

    def compile(self, *args, **kwargs) -> QoalaModule:
        # TODO - Implement (if needed) more functionality than just invoking the function
        # To ease the insertion of the statement into the program body, we need to
        # keep a reference to the current instance of the QoalaProgram we are compiling.
        # This does not allow parallel compilation, since instructions of different programs
        # would end in the same body, of a single function.
        QoalaProgram._compiler_lock.acquire()
        QoalaProgram._instance = self
        # We clear the body of this qoala program.
        self._module.clear_body()
        ret_val = self._entry_fun(*args, **kwargs)
        self._is_compiled = True
        # We delete the reference to the QoalaProgram under compilation
        del QoalaProgram._instance
        QoalaProgram._compiler_lock.release()
        return ret_val
