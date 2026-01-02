import pytest

from qoala import QoalaProgram
from qoala.utils import debug_info as dbg_info
from qoala.ast.model import BlockPlaceholder, QoalaBlock
from qoala.ast.operations.branching import ConditionalBranching, UnconditionalBranching
from qoala.ast.operations.numeric import Add
from qoala.ast.operations.order import (
    EqualsOp,
    NotEqualsOp,
    LessThanOp,
    LessThanOrEqualsOp,
    GreaterThanOp,
    GreaterThanOrEqualsOp,
)
from qoala.ast.value import QoalaBool, QoalaInteger
from qoala.types.classical.booleans import Bool
from qoala.operations.branching import (
    if_cond,
    if_eq,
    if_neq,
    if_lt,
    if_le,
    if_gt,
    if_ge,
)
from qoala.types.classical import Int


class DummyQoalaProgram(QoalaProgram):
    pass


class TestBranchingSemantics:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name

    def test_branching_simple_if(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(self.test_branching_simple_if)
        QoalaProgram._instance._module.add_function(self.test_branching_simple_if)

        bool_true = Bool(True)
        branching = if_cond(bool_true)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, QoalaBool)
        assert branching.condition.value == True

        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(25)
                assert len(branch_false.operations) == 1
        # TODO - In the following "add" operation, the frontend captures the value of "a" **coming from the false
        #  branch** (20), so the value coming from true will never be captured in MLIR. The actual value is not
        #  known until runtime, but the frontend does not have a way to figure this out. This is a bug!!!
        #  In LLVM this issue is solved with "stack allocations", which return a *pointer* to the stack:
        #    %ptr_to_a = alloc i32 ;; This is a pointer to a portion of memory containing an i32 value
        #    %cond = cmpi eq %val_1, %val_2  ;; really doesn't matter
        #    cond_br %cond, ^bb1, ^bb2... ;; True -> ^bb1, False -> ^bb2
        #    ^bb1:
        #      store $4, %ptr_to_a
        #      br ^bb3
        #    ^bb2:
        #      store $5, %ptr_to_a
        #      br ^bb3
        #    ^bb3:
        #    %val_of_a = load %ptr_to_a : i32 ;;; "val_of_a" is 4 if %cond is true, 5 otherwise
        #  We need to find a way to emulate the same in this frontend (and translate it into MLIR)
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 6 ops: Bool(True), Cond_branch, Int(7), Int(4), LessThanOp, Cond_branch
        assert len(program_blocks[0].operations) == 6
        assert isinstance(program_blocks[0].operations[0], QoalaBool)
        assert isinstance(program_blocks[0].operations[1], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[2], QoalaInteger)
        assert isinstance(program_blocks[0].operations[3], QoalaInteger)
        assert isinstance(program_blocks[0].operations[4], LessThanOp)
        assert isinstance(program_blocks[0].operations[5], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)

    def test_branching_equals(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(self.test_branching_equals)
        QoalaProgram._instance._module.add_function(self.test_branching_equals)

        branching = if_eq(Int(4), 7)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, EqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 7

        with if_eq(Int(4), 7) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(25)
                assert len(branch_false.operations) == 1
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 8 ops: Int(4), Int(7), EqualsOp, Cond_branch, Int(7), Int(4), EqualsOp, Cond_branch
        assert len(program_blocks[0].operations) == 8
        assert isinstance(program_blocks[0].operations[0], QoalaInteger)
        assert isinstance(program_blocks[0].operations[1], QoalaInteger)
        assert isinstance(program_blocks[0].operations[2], EqualsOp)
        assert isinstance(program_blocks[0].operations[3], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[4], QoalaInteger)
        assert isinstance(program_blocks[0].operations[5], QoalaInteger)
        assert isinstance(program_blocks[0].operations[6], EqualsOp)
        assert isinstance(program_blocks[0].operations[7], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)

    def test_branching_not_equals(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(self.test_branching_not_equals)
        QoalaProgram._instance._module.add_function(self.test_branching_not_equals)

        branching = if_neq(Int(4), 7)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, NotEqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 7

        with if_neq(Int(4), 7) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(25)
                assert len(branch_false.operations) == 1
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 8 ops: Int(4), Int(7), NotEqualsOp, Cond_branch, Int(7), Int(4), NotEqualsOp, Cond_branch
        assert len(program_blocks[0].operations) == 8
        assert isinstance(program_blocks[0].operations[0], QoalaInteger)
        assert isinstance(program_blocks[0].operations[1], QoalaInteger)
        assert isinstance(program_blocks[0].operations[2], NotEqualsOp)
        assert isinstance(program_blocks[0].operations[3], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[4], QoalaInteger)
        assert isinstance(program_blocks[0].operations[5], QoalaInteger)
        assert isinstance(program_blocks[0].operations[6], NotEqualsOp)
        assert isinstance(program_blocks[0].operations[7], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)

    def test_branching_less_than(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(self.test_branching_less_than)
        QoalaProgram._instance._module.add_function(self.test_branching_less_than)

        branching = if_lt(Int(4), 7)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, LessThanOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 7

        with if_lt(Int(4), 7) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(25)
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 8 ops: Int(4), Int(7), LessThanOp, Cond_branch, Int(7), Int(4), LessThanOp, Cond_branch
        assert len(program_blocks[0].operations) == 8
        assert isinstance(program_blocks[0].operations[0], QoalaInteger)
        assert isinstance(program_blocks[0].operations[1], QoalaInteger)
        assert isinstance(program_blocks[0].operations[2], LessThanOp)
        assert isinstance(program_blocks[0].operations[3], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[4], QoalaInteger)
        assert isinstance(program_blocks[0].operations[5], QoalaInteger)
        assert isinstance(program_blocks[0].operations[6], LessThanOp)
        assert isinstance(program_blocks[0].operations[7], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)

    def test_branching_less_than_or_equals(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            self.test_branching_less_than_or_equals
        )
        QoalaProgram._instance._module.add_function(
            self.test_branching_less_than_or_equals
        )

        branching = if_le(Int(4), 7)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, LessThanOrEqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 7

        with if_le(Int(4), 7) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(15)
                assert len(branch_false.operations) == 1
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 8 ops: Int(4), Int(7), LessThanOrEqOp, Cond_branch, Int(7), Int(4), LessThanOrEqOp, Cond_branch
        assert len(program_blocks[0].operations) == 8
        assert isinstance(program_blocks[0].operations[0], QoalaInteger)
        assert isinstance(program_blocks[0].operations[1], QoalaInteger)
        assert isinstance(program_blocks[0].operations[2], LessThanOrEqualsOp)
        assert isinstance(program_blocks[0].operations[3], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[4], QoalaInteger)
        assert isinstance(program_blocks[0].operations[5], QoalaInteger)
        assert isinstance(program_blocks[0].operations[6], LessThanOrEqualsOp)
        assert isinstance(program_blocks[0].operations[7], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)

    def test_branching_greater_than(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(self.test_branching_greater_than)
        QoalaProgram._instance._module.add_function(self.test_branching_greater_than)

        branching = if_gt(Int(4), 7)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, GreaterThanOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 7

        with if_gt(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(15)
                assert len(branch_false.operations) == 1
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 8 ops: Int(4), Int(7), GreaterThanOp, Cond_branch, Int(7), Int(4), GreaterThanOp, Cond_branch
        assert len(program_blocks[0].operations) == 8
        assert isinstance(program_blocks[0].operations[0], QoalaInteger)
        assert isinstance(program_blocks[0].operations[1], QoalaInteger)
        assert isinstance(program_blocks[0].operations[2], GreaterThanOp)
        assert isinstance(program_blocks[0].operations[3], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[4], QoalaInteger)
        assert isinstance(program_blocks[0].operations[5], QoalaInteger)
        assert isinstance(program_blocks[0].operations[6], GreaterThanOp)
        assert isinstance(program_blocks[0].operations[7], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)

    def test_branching_greater_than_or_equals(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            self.test_branching_greater_than_or_equals
        )
        QoalaProgram._instance._module.add_function(
            self.test_branching_greater_than_or_equals
        )
        branching = if_ge(Int(4), 7)

        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, GreaterThanOrEqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 7

        with if_ge(Int(4), 7) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(15)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(15)
                assert len(branch_false.operations) == 1
        b = a + 10
        # We expect 4 blocks: entry (with conditional branch) -> true -> false -> terminal.
        assert len(QoalaProgram._instance.current_function().blocks) == 4
        # We also assert that there are no placeholder blocks on the final AST
        program_blocks = QoalaProgram._instance.current_function().blocks
        assert all([isinstance(block, QoalaBlock) for block in program_blocks])

        # Assert the types of ops of each block:
        # 1. 8 ops: Int(4), Int(7), GreaterThanOrEqOp, Cond_branch, Int(7), Int(4), GreaterThanOrEqOp, Cond_branch
        assert len(program_blocks[0].operations) == 8
        assert isinstance(program_blocks[0].operations[0], QoalaInteger)
        assert isinstance(program_blocks[0].operations[1], QoalaInteger)
        assert isinstance(program_blocks[0].operations[2], GreaterThanOrEqualsOp)
        assert isinstance(program_blocks[0].operations[3], ConditionalBranching)
        assert isinstance(program_blocks[0].operations[4], QoalaInteger)
        assert isinstance(program_blocks[0].operations[5], QoalaInteger)
        assert isinstance(program_blocks[0].operations[6], GreaterThanOrEqualsOp)
        assert isinstance(program_blocks[0].operations[7], ConditionalBranching)
        # 2. 2 ops: Int(10), incond_branch to 4
        assert len(program_blocks[1].operations) == 2
        assert isinstance(program_blocks[1].operations[0], QoalaInteger)
        assert isinstance(program_blocks[1].operations[1], UnconditionalBranching)
        # 3. 2 ops: Int(20), incond_branch to 4
        assert len(program_blocks[2].operations) == 2
        assert isinstance(program_blocks[2].operations[0], QoalaInteger)
        assert isinstance(program_blocks[2].operations[1], UnconditionalBranching)
        # 4. 2 ops: Int(10), add operation
        assert len(program_blocks[3].operations) == 2
        assert isinstance(program_blocks[3].operations[0], QoalaInteger)
        assert isinstance(program_blocks[3].operations[1], Add)
