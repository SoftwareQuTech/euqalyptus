from dataclasses import dataclass
from . import QoalaCompilable, QoalaExpression
from typing import List, Optional

from qnet.dialects import qnet
from qnet.ir import Context, Location, Block, InsertionPoint, FunctionType

from qoala.utils.debug_info import DebugInfo
from qoala.errors import ValueUnknownAtCompileTimeError


@dataclass(init=False)
class BlockPlaceholder:
    _operations: List[QoalaExpression]
    _block_id: int
    """
    Placeholder for the "soon to be placed" blocks of a branching instruction.
    This class is intended to just contain the 
    """

    def __init__(self):
        self._operations = []
        self._block_id = -1

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    def append_to_block(self, expression: QoalaExpression):
        self.operations.append(expression)

    def __enter__(self):
        # Assign the block ID to this placeholder
        from qoala import QoalaProgram
        self._last_block_id = QoalaProgram.get_last_block_id()
        # If self._last_block_id == -1, then we're interpreting code *without* compiling it.
        # This is the case when testing syntax
        # TODO - Assign this placeholder block in the QoalaProgram instance
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Convert this placeholder into a real block
        new_block = QoalaBlock(self._last_block_id)
        for operation in self._operations:
            new_block.append_to_block(operation)
        # TODO - Insert the new block into the QoalaProgram instance


@dataclass(init=False)
class QoalaBlock(QoalaCompilable):
    # TODO - Rethink the types of the arguments, since they can be the arguments of a function.
    _block_id: int
    _args: List[QoalaExpression]
    _operations: List[QoalaExpression]
    _qnet_function: Optional[qnet.FuncOp]
    _qnet_block: Optional[Block]
    debug_info: DebugInfo

    def __init__(self, block_id: int):
        self._block_id = block_id
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
        if self._block_id == 0:
            # If the block has position "0", we create it at the beginning of the body
            # TODO - Deal with the arguments of the function, which need to match the block arguments
            block = Block.create_at_start(self._qnet_function.body)
        else:
            # In any other case, we get the last block, and create a new one right after
            # TODO - Add arguments top the block, when needed
            last_block = self._qnet_function.body.blocks[-1]
            block = last_block.create_after()
        self._qnet_block = block
        with InsertionPoint(block):
            for operation in self._operations:
                operation.compile(ctx)
        pass


@dataclass(init=False)
class QoalaFunction(QoalaCompilable):
    # Functions do not have a list or arguments, since the *first block* will contain that information
    _blocks: List[QoalaBlock]
    _current_block: QoalaBlock | BlockPlaceholder
    _function_name: str
    debug_info: DebugInfo

    def __init__(self, name: str):
        self._blocks = []
        self._function_name = name
        # We start with a single empty block
        self.emplace_new_empty_block()

    def emplace_new_empty_block(self):
        self._current_block = QoalaBlock(len(self._blocks))
        self._blocks.append(self._current_block)

    @property
    def blocks(self) -> List[QoalaBlock]:
        return self._blocks

    def append_to_current_block(self, expression: QoalaExpression):
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
