from dataclasses import dataclass
from typing import List

from qoala.ast import QoalaASTElement

from qoalahir.ir import *
from qoalahir.dialects import hir, func, builtin


@dataclass(init=False)
class QoalaModule:
    _body: List[QoalaASTElement]
    _function_name: str
    _qir_module: Module

    def __init__(self, function_name: str):
        self._body = []
        self._function_name = function_name

    def clear_body(self):
        self._body.clear()

    def add_element_to_body(self, elem: QoalaASTElement):
        self._body.append(elem)

    @property
    def asm(self) -> str:
        self._init_qir_module()
        return str(self._qir_module)

    def __str__(self) -> str:
        return self.asm

    def _init_qir_module(self) -> None:
        with Context() as ctx, Location.unknown():
            hir.register_dialect(ctx)
            qir_module = Module.create()
            with InsertionPoint(qir_module.body):
                func_type = FunctionType.get(inputs=[], results=[])
                function = func.FuncOp(
                    name=f"{self._function_name}",
                    type=func_type,
                )
                block = Block.create_at_start(function.body)
                with InsertionPoint(block):
                    for operation in self._body:
                        operation.to_hir(ctx)
                    func.ReturnOp([])
            # Before closing the context, we save the ASM we just created
            self._qir_module = qir_module
