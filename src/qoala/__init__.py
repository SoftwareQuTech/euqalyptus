import types as py_types
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from threading import Lock
from typing import List, Self, Any, Dict, Tuple

import qoala.utils.debug_info as dbg_info
from qoala.ast import QoalaExpression
from qoala.errors import NotYetCompiledError, QuantumProgramNotImplementedError
from qoala.module import QoalaModule


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
        self._function_name = entry_fun.__name__
        module_dbg_info = dbg_info.get_debug_info_for_function(entry_fun)
        self._module = QoalaModule(self._function_name, module_dbg_info)
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
    def add_to_body(cls, item: QoalaExpression) -> None:
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
            # TODO - Change this ugly way to set the name of the function for the debugging info engine
            dbg_info.function_name = self._function_name
            QoalaProgram._compiler_lock.acquire()
            QoalaProgram._instance = self
            QoalaProgram._declared_remotes = {}
            # We clear the body of this qoala program.
            self._module.clear_body()
            ret_val = self._entry_fun(*args, **kwargs)
            self._module.remotes = [remote for _, remote in self._declared_remotes.items()]
            self._is_compiled = True
            # We delete the reference to the QoalaProgram under compilation
            del QoalaProgram._instance
            return ret_val, self._module
        finally:
            QoalaProgram._compiler_lock.release()


class QoalaProgramBase(QoalaProgram, ABC):
    """
    Base class for Qoala programs. Any quantum internet program must
    be defined in a class that uses `QoalaProgram` as the base class.
    Programs that extend this class must implement the `main` method,
    which acts as the entry point of the program.
    WARNING: Due to how the constructor works, instances of subclasses
    of this class are instances of 'QoalaProgram' rather than
    'QoalaProgramBase', i.e.:
    ```
    class QProg(QoalaProgram):
        def main():
           #some code
    obj = QProg()
    assert not isinstance(obj, QoalaProgramBase)
    assert isinstance(obj, QoalaProgram)
    ```
    """

    @staticmethod
    def __main_not_implemented(clazz) -> bool:
        # Check that
        # * clazz has a "main" attriobute
        # * it is a function
        # * if "main" function has "__isabstrastmethod__" attribute is false
        if not hasattr(clazz, "main"):
            return False
        main_fn = getattr(clazz, "main")
        if type(main_fn) is py_types.MethodType:
            return False
        if hasattr(main_fn, "__isabstractmethod__"):
            return getattr(getattr(clazz, "main"), '__isabstractmethod__')
        else:
            return False

    def __new__(cls, *args, **kwargs):
        if QoalaProgramBase.__main_not_implemented(cls):
            raise QuantumProgramNotImplementedError(
                cls.__name__,
                f"Main function was not found in the class '{cls.__name__}'")
        # Black magic: create the instance, using the "main" function as the
        # entry function
        instance = QoalaProgram(entry_fun=cls.main)
        # We override that, partially initializing the entry function with the instance (self) argument
        instance._entry_fun = partial(cls.main, instance)
        # We return the instance of the newly created object
        return instance

    @abstractmethod
    def main(self, *args: Any, **kwargs: Any) -> Any:
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
