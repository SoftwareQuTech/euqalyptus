from dataclasses import dataclass
from . import QoalaCompilable, QoalaExpression
from typing import List, Optional, Dict

from qnet.dialects import qnet
from qnet.ir import Context, Location, Block, InsertionPoint, FunctionType

from qoala.utils.debug_info import DebugInfo


@dataclass(init=False)
class QoalaBlock(QoalaCompilable):
    # TODO - Rethink the types of the arguments, since they can be the arguments of a function.
    _block_id: int
    _args: List[QoalaExpression]
    _operations: List[QoalaExpression]
    _qnet_function: Optional[qnet.FuncOp]
    _qnet_block: Optional[Block]
    _container_function: "QoalaFunction"
    debug_info: DebugInfo

    def __init__(self, block_id: int, qoala_function: "QoalaFunction"):
        self._block_id = block_id
        self._args = []
        self._operations = []
        self._container_function = qoala_function
        self._qnet_function = None
        self._qnet_block = None

    def __hash__(self):
        return hash(self._block_id)

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    def append_to_block(self, expression: QoalaExpression):
        self.operations.append(expression)
        expression.qoala_block = self

    @property
    def qnet_function(self) -> Optional[qnet.FuncOp]:
        return self._qnet_function

    @qnet_function.setter
    def qnet_function(self, qnet_function: qnet.FuncOp):
        self._qnet_function = qnet_function

    @property
    def qnet_block(self) -> Optional[Block]:
        return self._qnet_block

    @property
    def qoala_function(self) -> "QoalaFunction":
        return self._container_function

    def create_empty_qnet_block(self):
        if self._block_id == 0:
            # If the block has position "0", we create it at the beginning of the body
            # TODO - Deal with the arguments of the function, which need to match the block arguments
            block = Block.create_at_start(self._qnet_function.body)
        else:
            # In any other case, we get the last block, and create a new one right after
            # TODO - Add arguments top the block, when needed
            last_block_number = len(self._qnet_function.body.blocks) - 1
            last_block = self._qnet_function.body.blocks[last_block_number]
            block = last_block.create_after()
        self._qnet_block = block

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        with InsertionPoint(self._qnet_block):
            for operation in self._operations:
                operation.compile(ctx)


@dataclass(init=False)
class BranchingBlockPlaceholder:
    _operations: List[QoalaExpression]
    _block_id: int
    _branch_operation: "ConditionalBranching"
    _join_dest: QoalaBlock
    _container_function: "QoalaFunction"

    """
    Placeholder for the "soon to be placed" blocks of a branching instruction.
    This class is intended to just contain the operations and some extra information
    used to correctly insert the block references for the branching instruction.
    """

    def __init__(
        self, block_id: int, condition: "ConditionalBranching", join_dest: QoalaBlock, qoala_function: "QoalaFunction"
    ):
        self._operations = []
        self._block_id = block_id
        self._branch_operation = condition
        self._join_dest = join_dest
        self._container_function = qoala_function

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    def append_to_block(self, expression: QoalaExpression):
        self.operations.append(expression)

    def __enter__(self):
        from qoala import QoalaProgram

        # Mark this placeholder block as active in the QoalaProgram instance
        QoalaProgram.current_function().mark_as_current_block(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Convert this placeholder into a real block
        from qoala.ast.operations.branching import UnconditionalBranching

        self.append_to_block(UnconditionalBranching(self._join_dest))
        new_block = QoalaBlock(self._block_id, self._container_function)
        for operation in self._operations:
            new_block.append_to_block(operation)
        # Replace the placeholder in the enclosing branching operation
        if self is self._branch_operation._branch_true:
            self._branch_operation.true_dest = new_block
        elif self is self._branch_operation._branch_false:
            self._branch_operation.false_dest = new_block
        else:
            raise RuntimeError(
                f"Trying to replace a Block placeholder which is not attached to a branch op"
            )
        # Replace the placeholder in the function itself
        from qoala import QoalaProgram

        QoalaProgram.current_function().replace_placeholder_block(new_block, self)


@dataclass(init=False)
class QoalaFunction(QoalaCompilable):
    # Functions do not have a list or arguments, since the *first block* will contain that information
    _blocks: List[QoalaBlock | BranchingBlockPlaceholder]
    _current_block: QoalaBlock | BranchingBlockPlaceholder
    _function_name: str
    _block_map: Dict[QoalaBlock, Block]
    debug_info: DebugInfo

    def __init__(self, name: str):
        self._blocks = []
        self._function_name = name
        self._block_map = {}
        # We start with a single empty block
        self.emplace_new_empty_block()

    def replace_placeholder_block(
        self, new_block: QoalaBlock, placeholder: BranchingBlockPlaceholder
    ):
        block_position = -1
        for i, block in enumerate(self._blocks):
            if block is placeholder:
                block_position = i
        if block_position != -1:
            self._blocks[block_position] = new_block
        else:
            raise RuntimeError("Unknown placeholder block")

    def emplace_new_empty_block(self):
        self.emplace_block(QoalaBlock(len(self._blocks), self))

    def emplace_block(self, block: QoalaBlock | BranchingBlockPlaceholder):
        self._current_block = block
        self._blocks.append(block)

    def mark_as_current_block(self, block: QoalaBlock | BranchingBlockPlaceholder):
        self._current_block = block

    @property
    def blocks(self) -> List[QoalaBlock]:
        return self._blocks

    @property
    def blocks_map(self) -> Dict[QoalaBlock, Block]:
        return self._block_map

    def append_to_current_block(self, expression: QoalaExpression):
        self._current_block.append_to_block(expression)

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # Create the FuncOp object
        func_type = FunctionType.get(inputs=[], results=[], context=ctx)
        function = qnet.FuncOp(
            name=f"{self._function_name}",
            type=func_type,
            loc=location,
        )
        # Eagerly create empty blocks that will be filled later.
        # This is needed when compiling the branching instructions, which require
        # forward block references.
        for block in self._blocks:
            # We need to set the function of the block, to correctly insert the new block
            block.qnet_function = function
            block.create_empty_qnet_block()
            self._block_map[block] = block.qnet_block
        # Compile each block fo the function
        for block in self._blocks:
            block.compile(ctx, location)
        # Insert the return, only in the last block
        with InsertionPoint(self._blocks[-1].qnet_block):
            qnet.ReturnOp([], loc=location)
