from dataclasses import dataclass
from typing import List

from qnet.dialects import qnet
from qnet.ir import *

from qoala.ast import QoalaExpression
from qoala.utils.debug_info import DebugInfo


@dataclass(init=False)
class QoalaModule:
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
        [self._remotes.append(new_remote) for new_remote in new_remotes]

    @property
    def generic_asm(self) -> str:
        if not self._is_initialized:
            self._init_qir_module()
        return str(self._qir_module.operation.get_asm(print_generic_op_form=True))

    @property
    def asm(self) -> str:
        if not self._is_initialized:
            self._init_qir_module()
        return str(self._qir_module.operation.get_asm())

    @property
    def asm_dbg(self) -> str:
        if not self._is_initialized:
            self._init_qir_module()
        return str(self._qir_module.operation.get_asm(enable_debug_info=True))

    def __str__(self) -> str:
        return self.asm

    def _init_qir_module(self) -> None:
        with Context() as ctx:
            base_location_info = Location.file(
                filename=self._module_dbg_info.filename,
                line=self._module_dbg_info.line_start,
                col=self._module_dbg_info.col_start,
                context=ctx
            )
            with base_location_info:
                qnet.register_dialect(ctx)
                qir_module = Module.create(loc=base_location_info)
                with InsertionPoint(qir_module.body):
                    for remote in self._remotes:
                        remote.to_ir(ctx)
                    func_type = FunctionType.get(inputs=[], results=[])
                    function = qnet.FuncOp(
                        name=f"{self._function_name}",
                        type=func_type,
                        loc=base_location_info
                    )
                    block = Block.create_at_start(function.body)
                    with InsertionPoint(block):
                        for operation in self._body:
                            operation.to_ir(ctx)
                        qnet.ReturnOp([], loc=base_location_info)
                # Before closing the context, we save the ASM we just created
                self._qir_module = qir_module
        self._is_initialized = True
