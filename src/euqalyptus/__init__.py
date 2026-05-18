import types as py_types
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from threading import Lock
from typing import List, Any, Dict, Tuple, Optional

from typing_extensions import Self

import euqalyptus.utils.debug_info as dbg_info
from euqalyptus.ast import QoalaExpression, QoalaFunction
from euqalyptus.errors import NotYetCompiledError, QuantumProgramNotImplementedError
from euqalyptus.module import QoalaModule

_compiler_lock: Lock = Lock()


@dataclass
class _CompilationOptions:
    lazy_compilation: bool = False
    use_singular_classical_comm_ops: bool = False


@dataclass
class CompilationContext:
    options: _CompilationOptions = field(default_factory=_CompilationOptions)


class QoalaProgram:
    """Decorator that turns a Python function into a Qoala program.

    Applying ``@QoalaProgram`` to a function marks it as a Qoala
    program. The decorator wraps the function in an object that
    exposes a :meth:`compile` method; calling ``compile()`` runs the
    decorated function under the SDK's recording mode and produces a
    :class:`QoalaModule` containing Qoala HIR.

    Example:
        ```python
        @QoalaProgram
        def my_function():
            q = LocalQubit()
            q.measure()

        _, module = my_function.compile()
        print(module.asm)
        ```

    Calling the decorated object is equivalent to calling
    ``.compile()`` on it; ``my_function()`` and ``my_function.compile()``
    both return the same ``(return_value, QoalaModule)`` tuple.
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
        """Get or set the class-level ``compile_lazy`` toggle.

        When set, subsequent calls to :meth:`compile` skip the
        MLIR-emission stage by default and build only the internal
        pseudo-AST. Useful in tests and repeated-compilation harnesses.

        Args:
            new_flag_value: When not ``None``, sets the toggle to this
                value. When ``None`` (the default), only reads the
                current value.

        Returns:
            The current value of the toggle (after the optional set).
        """
        if new_flag_value is not None:
            cls._compilation_context.options.lazy_compilation = new_flag_value
        return cls._compilation_context.options.lazy_compilation

    @classmethod
    def compile_singular_comm_ops(cls, new_flag_value: Optional[bool] = None) -> bool:
        """Get or set the class-level ``singular_comm_ops`` toggle.

        When set, subsequent calls to :meth:`compile` emit the scalar
        HIR ops (``qnet.send_int``, ``qnet.send_float``) for
        single-value classical sends instead of their tensor-form
        counterparts. The flag does not affect receives — see
        :meth:`compile` for the full discussion.

        Args:
            new_flag_value: When not ``None``, sets the toggle to this
                value. When ``None`` (the default), only reads the
                current value.

        Returns:
            The current value of the toggle (after the optional set).
        """
        if new_flag_value is not None:
            cls._compilation_context.options.use_singular_classical_comm_ops = (
                new_flag_value
            )
        return cls._compilation_context.options.use_singular_classical_comm_ops

    @property
    def module(self) -> QoalaModule:
        """The compiled :class:`QoalaModule`.

        Returns:
            The module produced by the most recent successful call to
            :meth:`compile`.

        Raises:
            NotYetCompiledError: If :meth:`compile` has not yet been
                called (or has not returned successfully) on this
                program.
        """
        if not self._is_compiled:
            raise NotYetCompiledError(
                "The program has not been compiled yet. Did you invoke 'compile()' on it?"
            )
        else:
            return self._module

    @classmethod
    def current_function(cls) -> QoalaFunction:
        """Return the :class:`QoalaFunction` currently being built.

        Used by the SDK constructors to find the function they should
        record into; rarely useful in user code.

        Returns:
            The active program's current function.

        Raises:
            RuntimeError: If no program is currently being compiled.
        """
        if hasattr(cls, "_instance"):
            return cls._instance._module.current_function  # type: ignore[no-any-return]
        # This should never happen
        raise RuntimeError(f"Program with no instance!")

    @classmethod
    def get_declared_remote(cls, remote_name: str) -> Any:
        """Look up a previously declared remote by name.

        Args:
            remote_name: The symbolic name of the remote peer.

        Returns:
            The :class:`DeclaredRemote` object for ``remote_name`` if
            one was declared in the current compilation, otherwise
            ``None``.
        """
        if remote_name in QoalaProgram._declared_remotes:
            return QoalaProgram._declared_remotes[remote_name]
        else:
            return None

    @classmethod
    def add_declared_remote(cls, remote_name: str, remote: Any) -> None:
        """Register a remote-peer declaration in the current compilation.

        Used internally by :class:`~euqalyptus.operations.Remote` to
        record a new alias; user code should call ``Remote("Name")``
        instead.

        Args:
            remote_name: The symbolic name of the remote.
            remote: The :class:`DeclaredRemote` AST node to associate
                with ``remote_name``.

        Raises:
            RuntimeError: If a remote with the same name has already
                been declared in this compilation.
        """
        if remote_name in QoalaProgram._declared_remotes:
            raise RuntimeError(
                f"A remote with name '{remote_name}' was already declared"
            )
        else:
            QoalaProgram._declared_remotes[remote_name] = remote

    def __call__(self, *args: Any, **kwargs: Any) -> Tuple[int, QoalaModule]:
        """Invoke :meth:`compile` directly on the decorated program.

        Calling the decorated object is equivalent to calling
        ``.compile()`` on it, forwarding all positional and keyword
        arguments to the entry function. Returns the same
        ``(return_value, QoalaModule)`` tuple.
        """
        return self.compile(*args, **kwargs)

    def compile(
        self,
        /,
        *args: Any,
        compile_lazy: bool = False,
        singular_comm_ops: bool = False,
        **kwargs: Any,
    ) -> Tuple[int, QoalaModule]:
        """Compile the decorated program into a Qoala HIR module.

        ``compile()`` runs the decorated function under the SDK's
        recording mode, so every SDK call inside the function body is
        intercepted and recorded as an AST node rather than performing
        its nominal action. Once the function returns, the recorded
        AST is walked and emitted as MLIR via the ``qnet`` Python
        bindings, yielding a :class:`QoalaModule` whose ``.asm``
        property is the textual HIR consumable by ``qoala-opt``.

        ``compile()`` acquires a process-wide lock and uses class-level
        state on :class:`QoalaProgram` to track the program currently
        being compiled, so two programs cannot be compiled
        concurrently from the same process — calls serialize.

        Args:
            *args: Positional arguments forwarded to the entry
                function.
            compile_lazy: When ``True``, only the internal pseudo-AST
                is built; MLIR emission is skipped. Useful in tests
                that want to assert structural properties without
                paying the cost of emission. Defaults to ``False``.
            singular_comm_ops: When ``True``, classical sends that
                carry a single value are emitted as the scalar HIR
                ops (``qnet.send_int``, ``qnet.send_float``) instead
                of the default tensor-form variants
                (``qnet.send_ints``, ``qnet.send_floats``). This
                avoids generating tensor values in HIR and simplifies
                the downstream pipeline. The flag does not affect
                receives: ``recv_int`` and ``recv_float`` are
                first-class scalar SDK calls and always emit scalar
                HIR. Defaults to ``False``.
            **kwargs: Keyword arguments forwarded to the entry
                function.

        Returns:
            A tuple ``(return_value, module)`` where ``return_value``
            is whatever the entry function returned (often ``None``)
            and ``module`` is the compiled :class:`QoalaModule`.
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
            QoalaProgram._instance = self  # type: ignore[misc]
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
            del QoalaProgram._instance  # type: ignore[misc]
            return ret_val, self._module
        finally:
            _compiler_lock.release()


class QoalaProgramBase(QoalaProgram, ABC):
    """Class-based alternative to the ``@QoalaProgram`` decorator.

    Subclass ``QoalaProgramBase`` and implement the abstract
    :meth:`main` method to define a Qoala program. Instantiating the
    subclass and calling ``.compile()`` runs ``main`` under the SDK's
    recording mode, just like the decorator form.

    Example:
        ```python
        class MyProgram(QoalaProgramBase):
            def main(self):
                q = LocalQubit()
                q.measure()

        program = MyProgram()
        _, module = program.compile()
        ```

    Warning:
        Due to the way ``__new__`` is wired, an instance of a subclass
        of ``QoalaProgramBase`` is not an instance of
        ``QoalaProgramBase`` — it is an instance of
        :class:`QoalaProgram`. Do not rely on
        ``isinstance(obj, QoalaProgramBase)``.
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
        instance._entry_fun = partial(cls.main, instance)  # type: ignore[arg-type]
        # We return the instance of the newly created object
        return instance

    @abstractmethod
    def main(self, *args: Any, **kwargs: Any) -> Any:
        """Entry point of a class-based Qoala program.

        Subclasses must implement this method. Inside its body you can
        use any quantum or classical primitive from the
        ``euqalyptus`` package — types, qubit operations, communication,
        and control-flow constructs — just as you would inside a
        ``@QoalaProgram`` decorated function.

        Args:
            *args: Positional arguments forwarded by
                :meth:`QoalaProgram.compile`.
            **kwargs: Keyword arguments forwarded by
                :meth:`QoalaProgram.compile`.

        Returns:
            Whatever value the program wants to return to the caller
            (typically classical measurement outcomes or ``None``).
            The returned value becomes the first element of the
            ``(return_value, QoalaModule)`` tuple from
            :meth:`compile`.
        """
