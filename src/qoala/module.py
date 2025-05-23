from dataclasses import dataclass
from typing import List

from qnet.dialects import qnet
from qnet.ir import Module, Context, Location, InsertionPoint, FunctionType, Block

from qoala.ast import QoalaExpression
from qoala.utils.debug_info import DebugInfo


@dataclass(init=False)
class QoalaModule:
    """
    Class representing a Qoala HIR module. An object of this class is returned when invoking
    the `compile` method on the qoala program. This class contains the `asm` property to get
    a string representation of the Qoala HIR module. The user can also access this
    representation using the `str()` method.
    """

    _body: List[QoalaExpression]
    _remotes: List[QoalaExpression]
    _module_dbg_info: DebugInfo
    _function_name: str
    _qir_module: Module
    _is_initialized: bool

    def __init__(self, function_name: str, module_dbg_info: DebugInfo):
        self._body = []
        self._function_name = function_name
        self._module_dbg_info = module_dbg_info
        self._is_initialized = False
        self._remotes = []

    def clear_body(self):
        self._body.clear()

    def add_element_to_body(self, elem: QoalaExpression):
        self._body.append(elem)

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
                    for remote in self._remotes:
                        remote.compile(ctx)
                    func_type = FunctionType.get(inputs=[], results=[], context=ctx)
                    function = qnet.FuncOp(
                        name=f"{self._function_name}",
                        type=func_type,
                        loc=base_location_info,
                    )
                    block = Block.create_at_start(function.body)
                    with InsertionPoint(block):
                        for operation in self._body:
                            operation.compile(ctx)
                        qnet.ReturnOp([], loc=base_location_info)
                # Before closing the context, we save the ASM we just created
                self._qir_module = qir_module
        self._is_initialized = True
