from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Type, TypeVar, Generic
from uuid import uuid4

from qnet.dialects import qnet, scf
from qnet.ir import Context, Operation, Location, Block, InsertionPoint, FunctionType

from qoala.ast.operations import with_arith_operators, with_bool_operators, with_order_operators
from qoala.errors import ExpressionNotAllowedInBlockError, AssignationError
from qoala.utils.debug_info import DebugInfo, get_debug_info
from qoala.ast import QoalaCompilable, QoalaExpression

_NumericValue = TypeVar("_NumericValue", "QoalaInteger",  "QoalaFloat", "QoalaBool")
_AllowedExprType = TypeVar("_AllowedExprType", bound=QoalaExpression)


@dataclass(init=False)
class QoalaScopedVal(ABC):
    _id: str

    def __hash__(self):
        return hash(self._id)

    @abstractmethod
    def get_current_value(self) -> QoalaExpression:
        pass


# TODO - Do we need these decorators to support the "use as a value"?
#  We might need a generic one (that captures all the dunder methods), that extracts
#  the real value (coming from the scf.if).
@with_arith_operators
@with_bool_operators
@with_order_operators
@dataclass(init=False)
class QoalaRuntimeValue(QoalaExpression, QoalaScopedVal, Generic[_NumericValue]):
    _type: _NumericValue
    _values: List[_NumericValue]

    def __init__(self):
        super().__init__()
        self._values = []
        self._type = None
        self._id = str(uuid4())
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        self._containing_block = QoalaProgram.current_function().current_block
        self._containing_block.scope.add_value_in_scope(self)

    def assign(self, value: _NumericValue):
        # When we assign a value to the runtime value, we check the type of any
        # other already-assigned value. If it matches, we attach the value to the
        # tracked values. This is needed to retrieve the "last value" when returning
        # the value outside the branch.
        if len(self._values) <= 0:
            self._type = type(value)
        if type(value) != self._type:
            raise AssignationError("Assigning a value to a scoped variable of another type")
        self._values.append(value)

    def get_current_value(self) -> QoalaExpression:
        return self._values[-1]

    def can_evaluate_to(self, cls) -> bool:
        from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaBool

        return cls == QoalaInteger or cls == QoalaBool or cls == QoalaFloat

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Think whether this class needs to be compiled to something or not.
        pass


class QoalaRuntimeQubit(QoalaExpression, QoalaScopedVal):
    def __init__(self):
        super().__init__()
        self._id = str(uuid4())
        self.debug_info = get_debug_info()

    def assign(self, value: "QoalaQubit"):
        pass

    def can_evaluate_to(self, cls) -> bool:
        from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaBool

        return cls == QoalaInteger or cls == QoalaBool or cls == QoalaFloat

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # TODO - Think whether this class needs to be compiled to something or not.
        pass


@dataclass(init=False)
class QoalaScope:
    """
    Defines a scope for values to be defined within. Any value defined will be
    attached to a scope.
    When a value needs to be retrieved (the ir_value), we should resolve it
    depending on whether if it is within the scope (direct line of sight) or
    if it needs to be "exported" from a sibling scope.

    Some scopes might be "locked", either up- or downwards. This means that the
    values defined within this scope cannot be "exported" to outside scopes; if
    locked upwards, then values cannot be returned to parent scopes. If locked
    downwards then values cannot be used in (grand*)children scopes.
    """
    # The structure to support scopes must be a tree:
    # * The initial scope must be defined at module level (maybe)
    # * One scope defined at function level
    # * One scope defined at "nesting" operations (if, for, while)
    # Once that a nesting level closes, the scope is closed (no mor values defined within)
    # If a new operation defines a new nesting level, then the "current" visible
    #  scope gets a new children scope and becomes the currently active.
    # New values are defined within the currently active scope
    # When generating IR, any referenced value *must* be resolved within the scope
    # tree:
    # * First, a bottom-up search: first in the current scope; then in all the direct parents.
    # * If not found, start a top-down.
    #   * If not found, the value is not defined.
    #   * If found, check if there is a *valid* path from the scope requesting the value
    #     until the one that contains it.
    #   * A path is deemed "valid" iff all the scopes that the value need to go through
    #     are not locked up- or downwards as needed.
    # TODO - Implement the scope

    _values_in_scope: List[QoalaScopedVal]
    _block: "QoalaBlock"

    def __init__(self, block: "QoalaBlock"):
        self._block = block
        self._values_in_scope = []

    @property
    def values(self) -> List[QoalaScopedVal]:
        return self._values_in_scope

    def add_value_in_scope(self, value: QoalaScopedVal):
        self._values_in_scope.append(value)

    def get_value(self, expr: QoalaExpression) -> Optional[Operation]:
        # TODO - Revisit if we need this method
        # Returns a value in the current scope. If not found here, search for it in the parents recursively.
        if expr in self._values_in_scope:
            return self._values_in_scope[expr]
        else:
            if self._block.scope is None:
                return None
            return self._block.scope.get_value(expr)


@dataclass(init=False)
class QoalaBranchTerminator(QoalaExpression):
    """
    Simple class that can be compiled into a scf.yield operation. These operations
    are *always* needed as block terminators, even if the scf.if block does not
    yield a value (in which case, this operation will not be printed in the simplified
    version of the IR).
    """

    _values_to_yield: List[QoalaExpression]

    def __init__(self, containing_block: "QoalaBlock", values_to_yield: List[QoalaExpression]):
        super().__init__()
        self._containing_block = containing_block
        self._values_to_yield = values_to_yield
        self.debug_info = get_debug_info()

    def can_evaluate_to(self, cls) -> bool:
        return False

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        self._ir_vals = scf.yield_((value for value in self._values_to_yield))


@dataclass(init=False)
class QoalaBlock(QoalaCompilable, Generic[_AllowedExprType]):
    # TODO - Rethink the types of the arguments, since they can be the arguments of a function.
    _block_id: int
    _args: List[QoalaExpression]
    _operations: List[QoalaExpression]
    _qnet_function: Optional[qnet.FuncOp]
    _qnet_block: Optional[Block]
    _container_function: "QoalaFunction"
    _allowed_types: List[Type[_AllowedExprType]]
    _values_to_yield: List[QoalaExpression]
    _branching_operation: "ConditionalBranching"  # Will be "None" in the main block of a function
    _scope: QoalaScope
    debug_info: DebugInfo

    def __init__(self, block_id: int, branch_op: "ConditionalBranching", qoala_function: "QoalaFunction"):
        self._block_id = block_id
        self._args = []
        self._operations = []
        self._container_function = qoala_function
        self._allowed_types = []
        self._qnet_function = None
        self._qnet_block = None
        self._scope = QoalaScope(self)
        self._values_to_yield = []
        self._branching_operation = branch_op
        self.debug_info = qoala_function.debug_info

    def __hash__(self):
        return hash(self._block_id)

    def __enter__(self):
        from qoala import QoalaProgram

        QoalaProgram.current_function().lift_type_restrictions_in_current_block()
        QoalaProgram.current_function().nest_block(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # We *need* to insert a block terminator, even if we don't return any
        # outside the scope of the if-then-else operation
        self._operations.append(QoalaBranchTerminator(self, self._values_to_yield))
        self._branching_operation.yielded_values = self._values_to_yield
        from qoala import QoalaProgram

        QoalaProgram.current_function().restrict_current_block(QoalaRuntimeValue)
        QoalaProgram.current_function().restrict_current_block(QoalaRuntimeQubit)
        QoalaProgram.current_function().pop_previous_block()

    @property
    def scope(self) -> QoalaScope:
        return self._scope

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    @property
    def qnet_block(self) -> Optional[Block]:
        return self._qnet_block

    @qnet_block.setter
    def qnet_block(self, qnet_block: Block):
        self._qnet_block = qnet_block

    def yield_value(self, val: "ScopedVar | ScopedQubit"):
        # At runtime, the value passed must be a QoalaScopedVal (i.e. either a QoalaRuntimeValue
        # or a QoalaRuntimeQubit). The signature of this function lets the IDE accept the
        # programming-time static type.
        assert isinstance(val, QoalaScopedVal)
        # We simply lock attach the current value of the value as one of the values to
        # be returned by scf.yield
        value_to_yield = val.get_current_value()
        self._values_to_yield.append(value_to_yield)

    def append_to_block(self, expression: QoalaExpression):
        # Check if we're appending to a restricted block or not
        if len(self._allowed_types) > 0:
            if all([not isinstance(expression, allowed_type) for allowed_type in self._allowed_types]):
                raise ExpressionNotAllowedInBlockError(
                    "Trying to add an expression on a restricted block", self._allowed_types
                )
        self.operations.append(expression)
        expression.qoala_block = self

    def restrict_to_expressions(self, allowed_type: Type[_AllowedExprType]):
        self._allowed_types.append(allowed_type)

    def lift_type_restrictions(self):
        self._allowed_types = []

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        with InsertionPoint(self._qnet_block):
            for operation in self._operations:
                operation.compile(ctx)


@dataclass(init=False)
class QoalaFunction(QoalaCompilable):
    # Functions do not have a list or arguments, since the *first block* will contain that information
    _main_block: Optional[QoalaBlock]
    _block_nesting_path: List[QoalaBlock]
    _function_name: str
    _last_block_id: int
    debug_info: DebugInfo

    def __init__(self, name: str, dbg_info: DebugInfo | None = None):
        self._function_name = name
        self.debug_info = dbg_info
        # We start with a single empty block, since it is the main block of the function
        # we can pass "None" as the cond_branch argument.
        self._main_block = QoalaBlock(0, None,  self)
        self._last_block_id = 0
        self._block_nesting_path = []
        self.nest_block(self._main_block)

    def get_new_block_id(self):
        self._last_block_id += self._last_block_id
        return self._last_block_id

    @property
    def current_block(self) -> QoalaBlock:
        return self._block_nesting_path[-1]

    def nest_block(self, block: QoalaBlock):
        self._block_nesting_path.append(block)

    def pop_previous_block(self):
        self._block_nesting_path.pop()

    def append_to_current_block(self, expression: QoalaExpression):
        self.current_block.append_to_block(expression)

    def restrict_current_block(self, allowed_type: Type[_AllowedExprType]):
        self.current_block.restrict_to_expressions(allowed_type)

    def lift_type_restrictions_in_current_block(self):
        self.current_block.lift_type_restrictions()

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
