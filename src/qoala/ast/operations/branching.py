from dataclasses import dataclass
from typing import Optional, List, Any, Type

from mypy.stubgen import Iterable
from qnet.dialects import scf, qnet
from qnet.dialects._ods_common import get_op_result_or_op_results
from qnet.extras.types import i32, f32, bool as mlir_bool
from qnet.ir import Context, Location

from qoala.ast import QoalaExpression
from qoala.ast.model import (
    QoalaBlock,
    QoalaRuntimeQubit,
    QoalaRuntimeValue,
    QoalaScopedVal,
)
from qoala.ast.operations import QoalaOperation
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaBool


@dataclass(init=False)
class ConditionalBranching(QoalaOperation):
    condition: QoalaExpression
    # Branches need to be a *forward reference* to the place where the code will be
    _branch_true: QoalaBlock
    _branch_false: QoalaBlock
    _used_scoped_vals: List[QoalaRuntimeValue | QoalaRuntimeQubit]
    _yielded_values: List[QoalaExpression]

    def __init__(self, condition: QoalaExpression):
        super().__init__()
        self.condition = condition
        self._used_scoped_vals = []
        self._yielded_values = []
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def __enter__(self):
        from qoala import QoalaProgram

        # We create the basic blocks for this conditional branching
        current_function = QoalaProgram.current_function()
        self._branch_true = QoalaBlock(
            current_function.get_new_block_id(), self, current_function
        )
        self._branch_false = QoalaBlock(
            current_function.get_new_block_id(), self, current_function
        )
        # At the nesting level of the conditional branch, we only expect having
        # "variable declarations", either numeric or quantum.
        # Set the current block in a "locked mode", so no new expressions can be
        # attached to the block, but we allow QoalaRuntimeValue and QoalaRuntimeQubit.
        QoalaProgram.current_function().restrict_current_block(QoalaRuntimeQubit)
        QoalaProgram.current_function().restrict_current_block(QoalaRuntimeValue)
        # Finally, return the true and false branches
        return self._branch_true, self._branch_false

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Exiting the conditional branch context marks the finish of the
        # branching on CFG.
        # We lift any type restriction currently being enforced
        from qoala import QoalaProgram

        QoalaProgram.current_function().lift_type_restrictions_in_current_block()
        for used_scoped_val in self._used_scoped_vals:
            used_scoped_val.locked = True
        # Analyze the true and false branch. If this branching op has yielded values
        # _and_ the branch is empty, then we need to insert a dummy yield in the empty branch.
        if len(self._yielded_values) > 0:
            if len(self._branch_true) <= 0:
                self._branch_true.insert_dummy_yield_value(self._used_scoped_vals)
            if len(self._branch_false) <= 0:
                self._branch_false.insert_dummy_yield_value(self._used_scoped_vals)
        # We don't need to pop the last block, since it is done by the
        # __exit__ method (context manager) of the QoalaBlock object.
        pass

    def _insert_dummy_yield_value(self, block: QoalaBlock):
        pass

    def report_used_scoped_val(self, scoped_val: QoalaRuntimeValue | QoalaRuntimeQubit):
        if scoped_val not in self._used_scoped_vals:
            self._used_scoped_vals.append(scoped_val)

    @property
    def true_dest(self) -> QoalaBlock:
        assert isinstance(self._branch_true, QoalaBlock)
        return self._branch_true

    @true_dest.setter
    def true_dest(self, new_block: QoalaBlock):
        assert isinstance(new_block, QoalaBlock)
        self._branch_true = new_block

    @property
    def false_dest(self) -> QoalaBlock:
        assert isinstance(self._branch_false, QoalaBlock)
        return self._branch_false

    @false_dest.setter
    def false_dest(self, new_block: QoalaBlock):
        assert isinstance(new_block, QoalaBlock)
        self._branch_false = new_block

    @property
    def yielded_values(self):
        return self._yielded_values

    @yielded_values.setter
    def yielded_values(self, yielded_vals: List[QoalaExpression]):
        if len(yielded_vals) > 0:
            self._yielded_values.append(*yielded_vals)

    def _capture_scoped_values(self):
        for scoped_val in self._used_scoped_vals:
            if scoped_val.captured_expression is not None:
                scoped_val.captured_value = scoped_val.captured_expression.ir_value

    def _reset_scoped_values(self):
        for scoped_val in self._used_scoped_vals:
            if scoped_val is not None and scoped_val.captured_value is not None:
                assert scoped_val.captured_expression is not None
                scoped_val.captured_expression.ir_value = scoped_val.captured_value

    def can_evaluate_to(self, cls) -> bool:
        return False

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        return_types = []
        for scoped_val in self._used_scoped_vals:
            if isinstance(scoped_val, QoalaRuntimeValue):
                if scoped_val.type == QoalaInteger:
                    return_types.append(i32())
                elif scoped_val.type == QoalaFloat:
                    return_types.append(f32())
                elif scoped_val.type == QoalaBool:
                    return_types.append(mlir_bool())
                else:
                    raise RuntimeError("Unknown runtime value type")
            if isinstance(scoped_val, QoalaRuntimeQubit):
                return_types.append(qnet.QubitType.get(ctx))
        # Create the scf-IfOp object
        if_op = scf.IfOp(
            self.condition.ir_value,
            return_types,
            hasElse=len(self._branch_false.operations) >= 1,
            loc=source_location,
        )
        # "Compile" the captures values from the scoped vals
        for scoped_val in self._used_scoped_vals:
            if isinstance(scoped_val, QoalaRuntimeValue):
                scoped_val.compile(ctx, location)
        # Compile the then/else block, only if they have operations.
        self._capture_scoped_values()
        if len(self._branch_true.operations) >= 1:
            qnet_then_block = if_op.thenRegion.blocks[0]
            self._branch_true.qnet_block = qnet_then_block
            self._branch_true.compile(ctx, location)
        self._reset_scoped_values()
        if len(self._branch_false.operations) >= 1:
            qnet_else_block = if_op.elseRegion.blocks[0]
            self._branch_false.qnet_block = qnet_else_block
            self._branch_false.compile(ctx, location)
        self._reset_scoped_values()
        # Set the IR value for this conditional branching op
        branching_ir_vals = get_op_result_or_op_results(if_op)
        self._ir_vals = branching_ir_vals
        iterable_ir_vals: Iterable[Any]
        if not isinstance(branching_ir_vals, Iterable):
            iterable_ir_vals = [branching_ir_vals]
        else:
            iterable_ir_vals = branching_ir_vals
        # Manually map the ir values of the runtime values
        for runtime_val, ir_val in zip(self._used_scoped_vals, iterable_ir_vals):
            runtime_val.ir_value = ir_val
