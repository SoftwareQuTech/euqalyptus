from abc import ABC, abstractmethod
from collections.abc import Callable
from threading import Lock
from typing import List, Self, Any, Dict, Tuple

from qoala.ast import QoalaASTElement
from qoala.module import QoalaModule


class NotYetCompiledError(RuntimeError):
    pass


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
    It provides the `compile` method which prepares all the
    operations in the decorated function to be transformed to ASM.
    In general, the usage workflow would be like:
    ```
    @QoalaProgram
    def my_function():
        q = LocalQubit()
        q.measure()

    my_function.compile()
    print(my_function.asm)
    ```
    """
    _instance: Self
    _compiler_lock: Lock = Lock()
    _is_compiled: bool
    _declared_remotes: Dict[str, Any]

    def __init__(self, entry_fun: Callable):
        self._module = QoalaModule(entry_fun.__name__)
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
    def add_to_body(cls, item: QoalaASTElement) -> None:
        if hasattr(QoalaProgram, "_instance"):
            QoalaProgram._instance._module.add_element_to_body(item)

    @classmethod
    def get_declared_remote(cls, remote_name: str) -> Any:
        if remote_name in QoalaProgram._declared_remotes:
            return QoalaProgram._declared_remotes[remote_name]
        else:
            return None

    @classmethod
    def add_declared_remote(cls, remote_name: str, remote: Any) -> None:
        if remote_name in QoalaProgram._declared_remotes:
            raise RuntimeError(f"A remote with name '{remote_name}' was already declared")
        else:
            QoalaProgram._declared_remotes[remote_name] = remote

    def __call__(self, *args: Any, **kwargs: Any) -> Tuple[int, QoalaModule]:
        return self.compile(*args, **kwargs)

    def compile(self, *args: Any, **kwargs: Any) -> Tuple[int, QoalaModule]:
        # TODO - Implement (if needed) more functionality than just invoking the function
        # To ease the insertion of the statement into the program body, we need to
        # keep a reference to the current instance of the QoalaProgram we are compiling.
        # This does not allow parallel compilation, since instructions of different programs
        # would end in the same body, of a single function.
        try:
            QoalaProgram._compiler_lock.acquire()
            QoalaProgram._instance = self
            QoalaProgram._declared_remotes = {}
            # We clear the body of this qoala program.
            self._module.clear_body()
            ret_val = self._entry_fun(*args, **kwargs)
            self._is_compiled = True
            # We delete the reference to the QoalaProgram under compilation
            del QoalaProgram._instance
            return ret_val, self._module
        finally:
            QoalaProgram._compiler_lock.release()
