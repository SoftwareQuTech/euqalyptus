import pytest

from qoala import QoalaProgram
from qoala.utils import debug_info as dbg_info
from qoala.ast.model import QoalaBlock, QoalaBranchTerminator
from qoala.ast.operations.branching import ConditionalBranching
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
                a = Int(15)
            with branch_false:
                a = Int(25)
        # WARNING - This test uses values that depend on the actual branch taken, which is only known at
        # runtime. This feature is *not*  supported by the frontend just yet. See below.
        # TODO - In the following "add" operation, the frontend captures the value of "a" **coming from the false
        #  branch** (25), so the value coming from true (15) will never be captured in MLIR. The actual value is
        #  not known until runtime, but the frontend does not have a way to figure this out. This is a bug!!!
        #  In LLVM this issue is solved with "stack allocations", which return a *pointer* to the stack:
        #    %ptr_to_a = alloc i32 ;; Local variable: it is a pointer to the stack containing an i32 value
        #    %cond = cmpi eq %val_1, %val_2  ;; really doesn't matter
        #    cond_br %cond, ^bb1, ^bb2... ;; True -> ^bb1, False -> ^bb2
        #    ^bb1:
        #      store $4, %ptr_to_a  ;; store value 4 in ptr_to_a
        #      br ^bb3
        #    ^bb2:
        #      store $5, %ptr_to_a  ;; store value 5 in ptr_to_a
        #      br ^bb3
        #    ^bb3:
        #    %val_of_a = load %ptr_to_a : i32 ;;; "val_of_a" is 4 if %cond is true, 5 otherwise
        #  To see this in action, compile the following C code:
        #  int main(int argc, char **argv) {
        #      int a;
        #      if (argc < 2) {
        #          a = 4;
        #      } else {
        #          a = 5;
        #      }
        #      return a;
        #  }
        #  Compile it with: `clang -S -emit-llvm -o test.ll test.c`
        #  We need to find a way to emulate the same in this frontend (and translate it into MLIR)
        #  Idea: Maybe we can check how MLIR emulates this behavior in the cf dialect?
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 8 ops: Bool(true), Cond_branch, Int(7), Int(4), LessThanOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 8
        assert isinstance(main_block.operations[0], QoalaBool)
        assert isinstance(main_block.operations[1], ConditionalBranching)
        assert isinstance(main_block.operations[2], QoalaInteger)
        assert isinstance(main_block.operations[3], QoalaInteger)
        assert isinstance(main_block.operations[4], LessThanOp)
        assert isinstance(main_block.operations[5], ConditionalBranching)
        assert isinstance(main_block.operations[5].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[5].false_dest, QoalaBlock)
        true_branch = main_block.operations[5].true_dest
        false_branch = main_block.operations[5].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[6], QoalaInteger)
        assert isinstance(main_block.operations[7], Add)

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
                a = Int(15)
            with branch_false:
                a = Int(25)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 10 ops: Int(4), Int(7), EqualsOp, Cond_branch, Int(7), Int(4), EqualsOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 10
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], EqualsOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], EqualsOp)
        assert isinstance(main_block.operations[7], ConditionalBranching)
        assert isinstance(main_block.operations[7].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[7].false_dest, QoalaBlock)
        true_branch = main_block.operations[7].true_dest
        false_branch = main_block.operations[7].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[8], QoalaInteger)
        assert isinstance(main_block.operations[9], Add)

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
                a = Int(15)
            with branch_false:
                a = Int(25)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 10 ops: Int(4), Int(7), NotEqOp, Cond_branch, Int(7), Int(4), NotEqOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 10
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], NotEqualsOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], NotEqualsOp)
        assert isinstance(main_block.operations[7], ConditionalBranching)
        assert isinstance(main_block.operations[7].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[7].false_dest, QoalaBlock)
        true_branch = main_block.operations[7].true_dest
        false_branch = main_block.operations[7].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[8], QoalaInteger)
        assert isinstance(main_block.operations[9], Add)

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
                a = Int(15)
            with branch_false:
                a = Int(25)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 10 ops: Int(4), Int(7), LessThanOp, Cond_branch, Int(7), Int(4), LessThanOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 10
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], LessThanOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], LessThanOp)
        assert isinstance(main_block.operations[7], ConditionalBranching)
        assert isinstance(main_block.operations[7].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[7].false_dest, QoalaBlock)
        true_branch = main_block.operations[7].true_dest
        false_branch = main_block.operations[7].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[8], QoalaInteger)
        assert isinstance(main_block.operations[9], Add)

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
                a = Int(15)
            with branch_false:
                a = Int(15)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 10 ops: Int(4), Int(7), LessThanOrEqOp, Cond_branch, Int(7), Int(4), LessThanOrEqOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 10
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], LessThanOrEqualsOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], LessThanOrEqualsOp)
        assert isinstance(main_block.operations[7], ConditionalBranching)
        assert isinstance(main_block.operations[7].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[7].false_dest, QoalaBlock)
        true_branch = main_block.operations[7].true_dest
        false_branch = main_block.operations[7].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[8], QoalaInteger)
        assert isinstance(main_block.operations[9], Add)

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
                a = Int(15)
            with branch_false:
                a = Int(15)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 10 ops: Int(4), Int(7), GreaterThan, Cond_branch, Int(7), Int(4), GreaterThanOrEqOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 10
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], GreaterThanOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], GreaterThanOp)
        assert isinstance(main_block.operations[7], ConditionalBranching)
        assert isinstance(main_block.operations[7].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[7].false_dest, QoalaBlock)
        true_branch = main_block.operations[7].true_dest
        false_branch = main_block.operations[7].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[8], QoalaInteger)
        assert isinstance(main_block.operations[9], Add)

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
                a = Int(15)
            with branch_false:
                a = Int(15)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 10 ops: Int(4), Int(7), GreaterThanOrEqOp, Cond_branch, Int(7), Int(4), GreaterThanOrEqOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 10
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], GreaterThanOrEqualsOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], GreaterThanOrEqualsOp)
        assert isinstance(main_block.operations[7], ConditionalBranching)
        assert isinstance(main_block.operations[7].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[7].false_dest, QoalaBlock)
        true_branch = main_block.operations[7].true_dest
        false_branch = main_block.operations[7].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 2 operations: Int(15), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[8], QoalaInteger)
        assert isinstance(main_block.operations[9], Add)

    def test_branching_missing_false_branch(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            self.test_branching_missing_false_branch
        )
        QoalaProgram._instance._module.add_function(
            self.test_branching_missing_false_branch
        )

        with if_cond(Int(4) == 7) as (branch_true, branch_false):
            with branch_true:
                a = Int(25)
            # We deliberately don't have a "branch_false" (not used)
        b = Int(15) + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops of the main block:
        # 1. 7 ops: Int(4), Int(7), EqualsOp, Cond_branch, Int(10), Int(15), Add
        assert len(main_block.operations) == 7
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], EqualsOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[3].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[3].false_dest, QoalaBlock)
        true_branch = main_block.operations[3].true_dest
        false_branch = main_block.operations[3].false_dest
        # True block has 2 operations: Int(25), BlockTerminator
        assert len(true_branch.operations) == 2
        assert isinstance(true_branch.operations[0], QoalaInteger)
        assert isinstance(true_branch.operations[1], QoalaBranchTerminator)
        # False block has 0 operations (block unused)
        assert len(false_branch.operations) == 0
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], Add)

    def test_branching_missing_true_branch(self):
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            self.test_branching_missing_true_branch
        )
        QoalaProgram._instance._module.add_function(
            self.test_branching_missing_true_branch
        )

        with if_cond(Int(4) == 7) as (branch_true, branch_false):
            with branch_false:
                a = Int(25)
            # We deliberately don't have a "branch_true" (not used)
        b = Int(15) + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops of the main block:
        # 1. 7 ops: Int(4), Int(7), EqualsOp, Cond_branch, Int(10), Int(15), Add
        assert len(main_block.operations) == 7
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], EqualsOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[3].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[3].false_dest, QoalaBlock)
        true_branch = main_block.operations[3].true_dest
        false_branch = main_block.operations[3].false_dest
        # False block has 2 operations: Int(25), BlockTerminator
        assert len(false_branch.operations) == 2
        assert isinstance(false_branch.operations[0], QoalaInteger)
        assert isinstance(false_branch.operations[1], QoalaBranchTerminator)
        # True block has 0 operations (block unused)
        assert len(true_branch.operations) == 0
        # Rest of the ops of the main block
        assert isinstance(main_block.operations[4], QoalaInteger)
        assert isinstance(main_block.operations[5], QoalaInteger)
        assert isinstance(main_block.operations[6], Add)
