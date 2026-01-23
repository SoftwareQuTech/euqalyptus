from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Type, TypeVar, Generic
from uuid import uuid4

from qnet.dialects import qnet, scf
from qnet.ir import Context, Location, Block, InsertionPoint, FunctionType

from qoala.ast.operations import (
    with_arith_operators,
    with_bool_operators,
    with_order_operators,
)
from qoala.ast.qubit import QubitBaseOperations, QoalaQubit
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaBool
from qoala.errors import ExpressionNotAllowedInBlockError, AssignationError
from qoala.utils.debug_info import DebugInfo, get_debug_info
from qoala.ast import QoalaCompilable, QoalaExpression

_NumericValue = TypeVar("_NumericValue", QoalaInteger, QoalaFloat, QoalaBool)
_AllowedExprType = TypeVar("_AllowedExprType", bound=QoalaExpression)


def hook_quantum_method(clazz):
    def qubit_method_wrapper(method_name: str):
        def method_impl(self, *args, **kwargs):
            return self._quantum_method_hook(method_name, *args, **kwargs)

        return method_impl

    qubit_methods = [
        "measure",
        "X",
        "Y",
        "Z",
        "T",
        "H",
        "K",
        "S",
        "rot_X",
        "rot_Y",
        "rot_Z",
        "cnot",
        "cphase",
        "cz",
        "free",
    ]
    for qubit_method in qubit_methods:
        setattr(clazz, qubit_method, qubit_method_wrapper(qubit_method))
    return clazz


@dataclass(init=False)
class QoalaScopedVal(ABC):
    _id: str
    _locked: bool
    _captured_expression: QoalaExpression | None
    _captured_value: qnet.Operation | None

    def __init__(self):
        self._locked = False
        self._id = str(uuid4())
        self._captured_value = None

    def __hash__(self):
        return hash(self._id)

    @property
    def captured_value(self) -> qnet.Operation | None:
        return self._captured_value

    @captured_value.setter
    def captured_value(self, value: qnet.Operation):
        self._captured_value = value

    @property
    def captured_expression(self) -> QoalaExpression | None:
        return self._captured_expression

    @captured_expression.setter
    def captured_expression(self, value: QoalaExpression):
        self._captured_expression = value

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, locked: bool):
        self._locked = locked

    @abstractmethod
    def get_current_value(self) -> QoalaExpression:
        pass


@with_arith_operators
@with_bool_operators
@with_order_operators
@dataclass(init=False)
class QoalaRuntimeValue(QoalaExpression, QoalaScopedVal, Generic[_NumericValue]):
    _type: Type[_NumericValue]
    _values: List[_NumericValue]

    def __init__(self, original_value: Optional[_NumericValue] = None):
        super().__init__()
        QoalaScopedVal.__init__(self)
        self._values = []
        self._captured_expression = original_value
        # This will be filled later
        self._type = None  # type: ignore[assignment]
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        self._containing_block = QoalaProgram.current_function().current_block

    @property
    def type(self) -> Type[_NumericValue]:
        return self._type

    def assign(self, value: _NumericValue):
        # When we assign a value to the runtime value, we check the type of any
        # other already-assigned value. If it matches, we attach the value to the
        # tracked values. This is needed to retrieve the "last value" when returning
        # the value outside the branch.
        if len(self._values) <= 0:
            self._type = type(value)
        if type(value) != self._type:
            raise AssignationError(
                "Assigning a value to a scoped variable of another type"
            )
        self._values.append(value)

    def get_current_value(self) -> QoalaExpression:
        return self._values[-1]

    def can_evaluate_to(self, cls) -> bool:
        return cls is self._type

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # We don't need to compile this object: It only acts as a container
        # used to capture the value when entering a branching operation
        pass


# The inheritance order is *very* important. This is needed to correctly refer to
# the super class when this object becomes "locked". The order defines the Method
# Resolution Order (MRO) for the "super()" reference.
@hook_quantum_method
@dataclass(init=False)
class QoalaRuntimeQubit(QubitBaseOperations, QoalaExpression, QoalaScopedVal):
    _operations: List[QoalaExpression]

    def __init__(self, qubit: QoalaQubit):
        QoalaExpression.__init__(self)
        QoalaScopedVal.__init__(self)
        self._captured_expression = qubit
        self._operations = []
        self.debug_info = get_debug_info()
        from qoala import QoalaProgram

        self._containing_block = QoalaProgram.current_function().current_block

    def _quantum_method_hook(
        self, method_name: str, *args, **kwargs
    ) -> QoalaExpression:
        # This method handles any quantum operation used on this "runtime qubit",
        # The idea here is to apply the quantum operation on the given qubit, but to
        # also keep track of any operation performed. This is needed to retrieve the
        # "last qubit value" when returning the value outside the branch.
        if self.locked:
            # Since "QubitBaseOperations" is the first class in the inheritance order
            # "super()" returns a proxy object whose MRO starts looking for
            # methods on "QubitBaseOperations".
            # This is important, since when the qubit is locked, we want to use "self"
            # as the qubit operand of the trapped method, so we need to invoke the
            # method fo "QubitBaseOperations".
            quantum_operation = getattr(super(), method_name)
        else:
            quantum_operation = getattr(self._captured_expression, method_name)
        op_expr: QoalaExpression = quantum_operation(*args, **kwargs)
        self._operations.append(op_expr)
        return op_expr

    def get_current_value(self) -> QoalaExpression:
        if self._locked:
            return self
        return self._operations[-1]

    def can_evaluate_to(self, cls) -> bool:
        from qoala.ast.qubit import QoalaQubit

        return cls is QoalaQubit

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        # We don't need to compile this object: It only acts as a container
        # used to capture the value when entering a branching operation
        pass


@dataclass(init=False)
class QoalaBranchTerminator(QoalaExpression):
    """
    Simple class that can be compiled into a scf.yield operation. These operations
    are *always* needed as block terminators, even if the scf.if block does not
    yield a value (in which case, this operation will not be printed in the simplified
    version of the IR).
    """

    _values_to_yield: List[QoalaExpression]

    def __init__(
        self, containing_block: "QoalaBlock", values_to_yield: List[QoalaExpression]
    ):
        super().__init__()
        self._containing_block = containing_block
        self._values_to_yield = values_to_yield
        self.debug_info = get_debug_info()

    def can_evaluate_to(self, cls) -> bool:
        return False

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        self._ir_vals = scf.yield_([value.ir_value for value in self._values_to_yield])


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
    # Will be "None" in the main block of a function
    _branching_operation: "ConditionalBranching"  # type: ignore[name-defined]
    debug_info: DebugInfo

    def __init__(
        self,
        block_id: int,
        branch_op: "ConditionalBranching",  # type: ignore[name-defined]
        qoala_function: "QoalaFunction",
    ):
        self._block_id = block_id
        self._args = []
        self._operations = []
        self._container_function = qoala_function
        self._allowed_types = []
        self._qnet_function = None
        self._qnet_block = None
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

    def __len__(self) -> int:
        return len(self._operations)

    def insert_dummy_yield_value(
        self, scoped_vals: List[QoalaRuntimeValue | QoalaRuntimeQubit]
    ):
        dummy_vals_to_yield: List[QoalaExpression] = []
        for scoped_val in scoped_vals:
            dummy_val: QoalaExpression
            if isinstance(scoped_val, QoalaRuntimeValue):
                if scoped_val.type is QoalaInteger:
                    dummy_val = QoalaInteger.from_immediate(
                        0, get_debug_info(), append_to_current_block=False
                    )
                elif scoped_val.type is QoalaFloat:
                    dummy_val = QoalaFloat.from_immediate(
                        0.0, get_debug_info(), append_to_current_block=False
                    )
                elif scoped_val.type is QoalaBool:
                    dummy_val = QoalaBool.from_immediate(
                        False, get_debug_info(), append_to_current_block=False
                    )
                else:
                    raise RuntimeError(
                        f"QoalaBlock: Cannot yield classical dummy value for type: '{scoped_val.type}'"
                    )
            elif isinstance(scoped_val, QoalaQubit):
                assert scoped_val.captured_expression is not None
                dummy_val = scoped_val.captured_expression
            else:
                raise RuntimeError(
                    f"QoalaBlock: Unknown yielded type from branch '{scoped_val}'"
                )
            self.append_to_block(dummy_val)
            dummy_vals_to_yield.append(dummy_val)
        terminator = QoalaBranchTerminator(self, dummy_vals_to_yield)
        self.append_to_block(terminator)

    @property
    def operations(self) -> List[QoalaExpression]:
        return self._operations

    @property
    def qnet_block(self) -> Optional[Block]:
        return self._qnet_block

    @qnet_block.setter
    def qnet_block(self, qnet_block: Block):
        self._qnet_block = qnet_block

    def yield_value(self, val: "ScopedVar | ScopedQubit"):  # type: ignore[name-defined]
        # At runtime, the value passed must be a QoalaScopedVal (i.e. either a QoalaRuntimeValue,
        # QoalaRuntimeQubit). The signature of this function lets the IDE accept the
        # programming-time static type.
        assert isinstance(val, QoalaScopedVal)
        # We simply lock attach the current value of the value as one of the values to
        # be returned by scf.yield
        self._branching_operation.report_used_scoped_val(val)
        value_to_yield = val.get_current_value()
        self._values_to_yield.append(value_to_yield)

    def append_to_block(self, expression: QoalaExpression):
        # Check if we're appending to a restricted block or not
        if len(self._allowed_types) > 0:
            if all(
                [
                    not isinstance(expression, allowed_type)
                    for allowed_type in self._allowed_types
                ]
            ):
                raise ExpressionNotAllowedInBlockError(
                    "Trying to add an expression on a restricted block",
                    self._allowed_types,
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
        self.debug_info = dbg_info  # type: ignore[assignment]
        # We start with a single empty block, since it is the main block of the function
        # we can pass "None" as the cond_branch argument.
        self._main_block = QoalaBlock(0, None, self)
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

        assert self._main_block is not None
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
