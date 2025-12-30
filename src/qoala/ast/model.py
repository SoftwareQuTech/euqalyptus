from dataclasses import dataclass
from . import QoalaCompilable, QoalaExpression
from typing import List, Optional

from qnet.dialects import qnet
from qnet.ir import Context, Location, Block, InsertionPoint, FunctionType

from qoala.utils.debug_info import DebugInfo


@dataclass(init=False)
class QoalaBlock(QoalaCompilable):
    # TODO - Rethink the types of the arguments, since they can be the arguments of a function.
    _position: int
    _args: List[QoalaExpression]
    _operations: List[QoalaExpression]
    _qnet_function: Optional[qnet.FuncOp]
    _qnet_block: Optional[Block]
    debug_info: DebugInfo

    def __init__(self, position: int):
        self._position = position
        self._args = []
        self._operations = []
        self._qnet_function = None
        self._qnet_block = None

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    def append_to_block(self, expression: QoalaExpression):
        self.operations.append(expression)

    @property
    def qnet_function(self) -> Optional[qnet.FuncOp]:
        return self._qnet_function

    @qnet_function.setter
    def qnet_function(self, qnet_function: qnet.FuncOp):
        self._qnet_function = qnet_function

    @property
    def qnet_block(self) -> Optional[Block]:
        return self._qnet_block

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # FIXME - THe block is *always* created at the start; this is not good when the
        #  function needs to have mor ethan one block
        block = Block.create_at_start(self._qnet_function.body)
        self._qnet_block = block
        with InsertionPoint(block):
            for operation in self._operations:
                operation.compile(ctx)
        pass


@dataclass(init=False)
class QoalaFunction(QoalaCompilable):
    # Functions do not have a list or arguments, since the *first block* will contain that information
    _blocks: List[QoalaBlock]
    _function_name: str
    debug_info: DebugInfo

    def __init__(self, name: str):
        self._blocks = []
        self._function_name = name
        # We start with a single empty block
        self.emplace_new_empty_block()

    def emplace_new_empty_block(self):
        self._blocks.append(QoalaBlock(len(self._blocks)))

    @property
    def blocks(self) -> List[QoalaBlock]:
        return self._blocks

    def append_to_function(self, expression: QoalaExpression):
        self._blocks[-1].append_to_block(expression)

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # Create the FuncOp object
        func_type = FunctionType.get(inputs=[], results=[], context=ctx)
        function = qnet.FuncOp(
            name=f"{self._function_name}",
            type=func_type,
            loc=location,
        )
        # Compile each block fo the function
        for i, block in enumerate(self._blocks):
            # We need to set the function of the block, to correctly insert the new block
            block.qnet_function = function
            block.compile(ctx, location)
            # Insert the return, only in the last block
            if i == len(self._blocks) - 1:
                with InsertionPoint(block.qnet_block):
                    qnet.ReturnOp([], loc=location)
