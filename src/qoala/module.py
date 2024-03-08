from dataclasses import dataclass
from typing import List

from qoala.ast import QoalaASTElement

from qoalahir.ir import *
from qoalahir.dialects import hir, func


@dataclass
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

    def _init_qir_module(self) -> Module:
        with Context() as ctx, Location.unknown():
            hir.register_dialect(ctx)
            qir_module = Module.create()
            with InsertionPoint(qir_module.body):
                none_type = NoneType.get(ctx)
                func_type = FunctionType.get(inputs=[none_type], results=[none_type])
                function = func.FuncOp(
                    name=f"{self._function_name}",
                    type=func_type,
                )
                block = Block.create_at_start(function.body)
                with InsertionPoint(block):
                    # TODO - Insert the actual ASM in the module
                    #        An idea to achieve this is to invoke a function on each of the QoalaASTElement of _body
                    #        which will add the operation to the right insertion point
                    # qubit = hir.NewQubitOp().qout
                    # op = hir.HadamardOp(qubit)
                    pass
            # Before closing the context, we print the ASM we just created
            self._qir_module = qir_module
