from dataclasses import dataclass
from typing import List, Optional

from qnet.dialects import qnet, scf
from qnet.ir import Context, Location, Block, InsertionPoint, FunctionType

from qoala.utils.debug_info import DebugInfo
from . import QoalaCompilable, QoalaExpression


@dataclass(init=False)
class QoalaBranchTerminator(QoalaExpression):
    """
    Simple class that can be compiled into a scf.yield operation. These operations
    are *always* needed as block terminators, even if the scf.if block does not
    yield a value (in which case, this operation will not be printed in the simplified
    version of the IR)
    """

    def can_evaluate_to(self, cls) -> bool:
        return False

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        self._ir_vals = scf.yield_(())


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
        self.debug_info = qoala_function.debug_info

    def __hash__(self):
        return hash(self._block_id)

    def __enter__(self):
        from qoala import QoalaProgram

        QoalaProgram.current_function().nest_block(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # We *need* to insert a block terminator, even if we don't return any
        # outside the scope of the if-then-else operation
        self._operations.append(QoalaBranchTerminator())
        from qoala import QoalaProgram

        QoalaProgram.current_function().pop_previous_block()

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    @property
    def qnet_block(self) -> Optional[Block]:
        return self._qnet_block

    @qnet_block.setter
    def qnet_block(self, qnet_block: Block):
        self._qnet_block = qnet_block

    def append_to_block(self, expression: QoalaExpression):
        self.operations.append(expression)
        expression.qoala_block = self

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        with InsertionPoint(self._qnet_block):
            for operation in self._operations:
                operation.compile(ctx)


@dataclass(init=False)
class QoalaFunction(QoalaCompilable):
    # Functions do not have a list or arguments, since the *first block* will contain that information
    _main_block: Optional[QoalaBlock]
    _block_nesting_path: List[QoalaBlock]
    _current_block: QoalaBlock
    _function_name: str
    _last_block_id: int
    debug_info: DebugInfo

    def __init__(self, name: str, dbg_info: DebugInfo | None = None):
        self._function_name = name
        self.debug_info = dbg_info
        # We start with a single empty block
        self._main_block = QoalaBlock(0, self)
        self._last_block_id = 0
        self._block_nesting_path = []
        self.nest_block(self._main_block)

    def get_new_block_id(self):
        self._last_block_id += self._last_block_id
        return self._last_block_id

    def nest_block(self, block: QoalaBlock):
        self._block_nesting_path.append(self._main_block)
        self._current_block = block

    def pop_previous_block(self):
        old_block = self._block_nesting_path.pop()
        self._current_block = old_block

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

        qnet_main_block = Block.create_at_start(function.body)
        self._main_block.qnet_block = qnet_main_block
        self._main_block.compile(ctx, location)

        # Insert the default return only in the last block, and only if needed.
        #
        # NOTE:
        # Ideally, we would check whether the block already has a terminator by
        # querying the MLIR "IsTerminator" trait. However, the MLIR Python bindings
        # used here do not expose terminator traits (e.g., `is_terminator` or
        # `has_trait`) on operations or blocks.
        #
        # Therefore, we explicitly check whether the last MLIR operation in the
        # block is a qnet.ReturnOp. This is sufficient for now, since qnet.return
        # is currently the only terminator operation in the QNet dialect.
        b = self._main_block.qnet_block
        mlir_ops = list(b.operations)

        already_has_return = bool(mlir_ops) and isinstance(mlir_ops[-1], qnet.ReturnOp)

        if not already_has_return:
            with InsertionPoint(b):
                qnet.ReturnOp([], loc=location)
