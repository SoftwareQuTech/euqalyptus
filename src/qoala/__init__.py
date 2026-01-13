import types as py_types
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from threading import Lock
from typing import List, Any, Dict, Tuple, Optional

from typing_extensions import Self

import qoala.utils.debug_info as dbg_info
from qoala.ast import QoalaExpression
from qoala.ast.model import QoalaFunction, QoalaScope
from qoala.errors import NotYetCompiledError, QuantumProgramNotImplementedError
from qoala.module import QoalaModule

_compiler_lock: Lock = Lock()


@dataclass
class _CompilationOptions:
    lazy_compilation: bool = False
    use_singular_classical_comm_ops: bool = False


@dataclass
class CompilationContext:
    options: _CompilationOptions = field(default_factory=_CompilationOptions)


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
    _declared_remotes: Dict[str, Any]
    _compilation_context: CompilationContext

    def __init__(self, entry_fun: Callable):
        self._function_name = entry_fun.__name__
        self._module_dbg_info = dbg_info.get_debug_info_for_function(entry_fun)
        self._entry_fun = entry_fun
        self._is_compiled = False
        # Create the module
        self._module = QoalaModule(self._module_dbg_info)

    @classmethod
    def compile_lazy_flag(cls, new_flag_value: Optional[bool] = None) -> bool:
        if new_flag_value is not None:
            cls._compilation_context.options.lazy_compilation = new_flag_value
        return cls._compilation_context.options.lazy_compilation

    @classmethod
    def compile_singular_comm_ops(cls, new_flag_value: Optional[bool] = None) -> bool:
        if new_flag_value is not None:
            cls._compilation_context.options.use_singular_classical_comm_ops = (
                new_flag_value
            )
        return cls._compilation_context.options.use_singular_classical_comm_ops

    @property
    def module(self):
        if not self._is_compiled:
            raise NotYetCompiledError(
                "The program has not been compiled yet. Did you invoke 'compile()' on it?"
            )
        else:
            return self._module

    @classmethod
    def current_function(cls) -> QoalaFunction:
        if hasattr(cls, "_instance"):
            return cls._instance._module.current_function
        # This should never happen
        raise RuntimeError(f"Program with no instance!")

    @classmethod
    def current_scope(cls) -> QoalaScope:
        if hasattr(cls, "_instance"):
            return cls._instance._module.current_scope
        # This should never happen
        raise RuntimeError(f"Program with no instance!")

    @classmethod
    def get_declared_remote(cls, remote_name: str) -> Any:
        if remote_name in QoalaProgram._declared_remotes:
            return QoalaProgram._declared_remotes[remote_name]
        else:
            return None

    @classmethod
    def add_declared_remote(cls, remote_name: str, remote: Any) -> None:
        if remote_name in QoalaProgram._declared_remotes:
            raise RuntimeError(
                f"A remote with name '{remote_name}' was already declared"
            )
        else:
            QoalaProgram._declared_remotes[remote_name] = remote

    def __call__(self, *args: Any, **kwargs: Any) -> Tuple[int, QoalaModule]:
        return self.compile(*args, **kwargs)

    def compile(
        self,
        /,
        *args: Any,
        compile_lazy: bool = False,
        singular_comm_ops: bool = False,
        **kwargs: Any,
    ) -> Tuple[int, QoalaModule]:
        """
        Compiles the decorated program, generating a ``QoalaModule`` object containing the HIR representation
        of the program.
        The returned ``QoalaModule`` object can be printed (using python's ``print`` function) to object a
        text-based representation of the HIR that can be fed into the ``qoala-opt`` tool for further optimization
        and compilation.
        Note: Using the ``singular_comm_ops`` option generates send/recv_int_float operations that handle 1
        value at a time. This has the implication of generating *no tensor values*. This heavily simplifies
        the optimization process, avoiding lowering tensors/vectors to other types.
        Arguments:
            compile_lazy (bool): Whether to compile the program without generating HIR.
                Useful for testing the internal structure of the compilation (pseudo-AST).
            singular_comm_ops (bool): Whether to generate singular versions of the classical
                communication.
        Returns:
            A tuple containing an integer (the compilation result) and the compiled module
            (a ``QoalaModule`` object)
        """

        # TODO - Implement (if needed) more functionality than just invoking the function
        # To ease the insertion of the statement into the program body, we need to
        # keep a reference to the current instance of the QoalaProgram we are compiling.
        # This does not allow parallel compilation, since instructions of different programs
        # would end in the same body, of a single function.
        try:
            # TODO - Change this ugly way to set the name of the function for the debug info engine
            dbg_info.function_name = self._function_name
            _compiler_lock.acquire()
            QoalaProgram._instance = self
            QoalaProgram._declared_remotes = {}
            QoalaProgram._compilation_context = CompilationContext()
            # We save the compilation options
            self.compile_lazy_flag(compile_lazy)
            self.compile_singular_comm_ops(singular_comm_ops)

            # We clear the body of this qoala program.
            self._module.clear()
            # For the moment, we create the *only* function of the module
            self._module.add_function(self._function_name, self._module_dbg_info)
            # Then we start "executing" the entry function code, to generate the AST
            ret_val = self._entry_fun(*args, **kwargs)
            # Add the remotes declarations
            self._module.remotes = [
                remote for _, remote in self._declared_remotes.items()
            ]
            self._is_compiled = True
            # Finally, we generate the QoalaHIR from the AST
            if not self.compile_lazy_flag():
                self.module.generate_qoala_hir()
            # We delete the reference to the QoalaProgram under compilation
            del QoalaProgram._instance
            return ret_val, self._module
        finally:
            _compiler_lock.release()


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
        # * clazz has a "main" attribute
        # * it is a function
        # * if "main" function has "__isabstrastmethod__" attribute is false
        if not hasattr(clazz, "main"):
            return False
        main_fn = getattr(clazz, "main")
        if isinstance(main_fn, py_types.MethodType):
            return False
        if hasattr(main_fn, "__isabstractmethod__"):
            return getattr(getattr(clazz, "main"), "__isabstractmethod__", False)
        else:
            return False

    def __new__(cls, *args, **kwargs):
        if QoalaProgramBase.__main_not_implemented(cls):
            raise QuantumProgramNotImplementedError(
                cls.__name__,
                f"Main function was not found in the class '{cls.__name__}'",
            )
        # Black magic: create the instance, using the "main" function as the
        # entry function
        instance = QoalaProgram(entry_fun=cls.main)
        # We override that, partially initializing the entry function with the
        # instance (self) argument
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
