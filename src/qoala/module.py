from dataclasses import dataclass
from typing import List

from qnet.dialects import qnet
from qnet.ir import Module, Context, Location, InsertionPoint

from qoala import QoalaScope
from qoala.ast import QoalaExpression
from qoala.ast.model import QoalaFunction
from qoala.utils.debug_info import DebugInfo


@dataclass(init=False)
class QoalaModule:
    """
    Class representing a Qoala HIR module. An object of this class is returned when invoking
    the `compile` method on the qoala program. This class contains the `asm` property to get
    a string representation of the Qoala HIR module. The user can also access this
    representation using the `str()` method.
    """

    _functions: List[QoalaFunction]
    _remotes: List[QoalaExpression]
    _module_dbg_info: DebugInfo
    _qir_module: Module
    _is_initialized: bool
    _current_function: QoalaFunction
    _current_scope: QoalaScope

    def __init__(self, module_dbg_info: DebugInfo):
        self._functions = []
        self._module_dbg_info = module_dbg_info
        self._is_initialized = False
        self._remotes = []

    def clear(self):
        self._functions.clear()

    def add_function(self, name: str, dbg_info: DebugInfo | None = None):
        new_function = QoalaFunction(name, dbg_info)
        self._current_function = new_function
        self._functions.append(new_function)

    def remove_function(self, name: str):
        to_remove = None
        for function in self._functions:
            if function._function_name == name:
                to_remove = function
        if to_remove is not None:
            self._functions.remove(to_remove)
            del self._current_function

    @property
    def current_function(self) -> QoalaFunction:
        return self._current_function

    @property
    def current_scope(self) -> QoalaScope:
        return self._current_scope

    @current_scope.setter
    def current_scope(self, new_scope: QoalaScope):
        self._current_scope = new_scope

    @property
    def functions(self) -> List[QoalaFunction]:
        return self._functions

    @property
    def remotes(self):
        return self._remotes

    @remotes.setter
    def remotes(self, new_remotes: List[QoalaExpression]):
        # Uniqueness of the remote names is ensured by the QoalaProgram class
        # We assume that all the remotes have unique identifiers
        for new_remote in new_remotes:
            self._remotes.append(new_remote)

    @property
    def generic_asm(self) -> str:
        if not self._is_initialized:
            self.generate_qoala_hir()
        return str(self._qir_module.operation.get_asm(print_generic_op_form=True))

    @property
    def asm(self) -> str:
        if not self._is_initialized:
            self.generate_qoala_hir()
        return str(self._qir_module.operation.get_asm())

    @property
    def asm_dbg(self) -> str:
        if not self._is_initialized:
            self.generate_qoala_hir()
        return str(self._qir_module.operation.get_asm(enable_debug_info=True))

    def __str__(self) -> str:
        return self.asm

    def generate_qoala_hir(self) -> None:
        if self._is_initialized:
            return
        with Context() as ctx:
            base_location_info = Location.file(
                filename=self._module_dbg_info.filename,
                line=self._module_dbg_info.line_start,
                col=self._module_dbg_info.col_start,
                context=ctx,
            )
            with base_location_info:
                qnet.register_dialect(ctx)
                qir_module = Module.create(loc=base_location_info)
                with InsertionPoint(qir_module.body):
                    # Insert all remotes
                    for remote in self._remotes:
                        remote.compile(ctx)
                    # Insert each function
                    for function in self._functions:
                        function.compile(ctx, base_location_info)
                # Before closing the context, we save the ASM we just created
                self._qir_module = qir_module
        self._is_initialized = True
