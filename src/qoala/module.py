from dataclasses import dataclass
from typing import List

from qnet.dialects import qnet, func
from qnet.ir import *

from qoala.ast import QoalaASTElement


@dataclass(init=False)
class QoalaModule:
    _body: List[QoalaASTElement]
    _function_name: str
    _qir_module: Module
    _is_initialized: bool

    def __init__(self, function_name: str):
        self._body = []
        self._function_name = function_name
        self._is_initialized = False

    def clear_body(self):
        self._body.clear()

    def add_element_to_body(self, elem: QoalaASTElement):
        self._body.append(elem)

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

    def __str__(self) -> str:
        return self.asm

    def _init_qir_module(self) -> None:
        with Context() as ctx, Location.unknown():
            qnet.register_dialect(ctx)
            qir_module = Module.create()
            with InsertionPoint(qir_module.body):
                func_type = FunctionType.get(inputs=[], results=[])
                function = qnet.QoalaFunc(
                    name=f"{self._function_name}",
                    type=func_type,
                )
                block = Block.create_at_start(function.body)
                with InsertionPoint(block):
                    for operation in self._body:
                        operation.to_ir(ctx)
                    qnet.QoalaReturn([])
            # Before closing the context, we save the ASM we just created
            self._qir_module = qir_module
        self._is_initialized = True
