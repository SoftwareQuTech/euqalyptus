import pytest

from qoala import QoalaProgram, CompilationContext
from qoala.ast.model import (
    QoalaBlock,
    QoalaBranchTerminator,
    QoalaRuntimeValue,
    QoalaRuntimeQubit,
)
from qoala.ast.operations.branching import ConditionalBranching
from qoala.ast.operations.control_flow import ReturnResultsOp
from qoala.ast.operations.numeric import Add
from qoala.ast.operations.order import (
    EqualsOp,
    NotEqualsOp,
    LessThanOp,
    LessThanOrEqualsOp,
    GreaterThanOp,
    GreaterThanOrEqualsOp,
)
from qoala.ast.operations.quantum import QubitMeasure, XGate, YGate, HGate
from qoala.ast.qubit import QoalaLocalQubit, QoalaEprs
from qoala.ast.value import QoalaBool, QoalaInteger
from qoala.errors import ExpressionNotAllowedInBlockError, AssignationError
from qoala.operations import Remote
from qoala.operations.branching import (
    if_cond,
    if_eq,
    if_neq,
    if_lt,
    if_le,
    if_gt,
    if_ge,
)
from qoala.operations.control_flow import return_results
from qoala.types.classical import Int, Float, ScopedVar
from qoala.types.classical.booleans import Bool
from qoala.types.quantum import LocalQubit, ScopedQubit
from qoala.types.quantum.qubit import Entangle
from qoala.utils import debug_info as dbg_info
from tests.helpers_tests import DummyQoalaProgram


class TestBranchingSemantics:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info on initialization
        dbg_info.function_name = "setup_debug_info"
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            getattr(request.cls, request.node.originalname)
        )
        QoalaProgram._instance._module.add_function(request.node.name)
        # We now set the real function name, so we can obtain meaningful dbg info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name
        yield
        QoalaProgram._instance._module.remove_function(request.node.name)
        del QoalaProgram._instance

    def test_branching_simple_if(self):
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
        b = Int(30) + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops on the main block:
        # 1. 8 ops: Bool(true), Cond_branch, Int(7), Int(4), LessThanOp,
        #            Cond_branch, Int(10), Add
        assert len(main_block.operations) == 9
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
        assert isinstance(main_block.operations[7], QoalaInteger)
        assert isinstance(main_block.operations[8], Add)

    def test_branching_equals(self):
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

    def test_invalid_expression_in_block(self):
        with pytest.raises(ExpressionNotAllowedInBlockError) as error:
            with if_cond(Int(4) < 7) as (branch_true, branch_false):
                a = ScopedVar()
                invalid = Int(30)
                # Anything under this line, it will not even get translated into AST
                with branch_true:
                    x = Int(15)
                with branch_false:
                    y = Int(25)
            b = Int(30) + 10
        assert "Trying to add an expression on a restricted block" in str(error.value)

    def test_invalid_assignment_in_block(self):
        with pytest.raises(AssignationError) as error:
            with if_cond(Int(4) < 7) as (branch_true, branch_false):
                a = ScopedVar()
                with branch_true:
                    a.assign(Int(15))
                with branch_false:
                    # We can't assign a float to a scoped var used with Int
                    a.assign(Float(25.0))
            b = Int(30) + 10
        assert "Assigning a value to a scoped variable of another type" in str(
            error.value
        )

    # WARNING - The next tests might not be exhaustive enough to test all the scenarios where to use
    # a value coming from different conditional branches.
    def test_using_classical_value_from_branching(self):
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            a = ScopedVar()
            with branch_true:
                a.assign(Int(15))
                branch_true.yield_value(a)
            with branch_false:
                a.assign(Int(25))
                branch_false.yield_value(a)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops of the main block:
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], LessThanOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[3].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[3].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[3]
        assert len(conditional_branch_op.yielded_values) == 2
        assert isinstance(conditional_branch_op.yielded_values[0], QoalaInteger)
        assert conditional_branch_op.yielded_values[0].value == 15
        assert isinstance(conditional_branch_op.yielded_values[1], QoalaInteger)
        assert conditional_branch_op.yielded_values[1].value == 25

        assert isinstance(main_block.operations[5], Add)
        add_op = main_block.operations[5]
        assert isinstance(add_op.operand_a, QoalaRuntimeValue)
        assert isinstance(add_op.operand_b, QoalaInteger)

    def test_capture_classical_value_in_scoped_var(self):
        old_val = Int(0)
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            a = ScopedVar(old_val)  # Holds a classical value
            with branch_true:
                branch_true.yield_value(a)
            with branch_false:
                branch_false.yield_value(a)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops of the main block:
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], QoalaInteger)
        assert isinstance(main_block.operations[3], LessThanOp)
        assert isinstance(main_block.operations[4], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[4].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[4].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[4]
        assert len(conditional_branch_op.yielded_values) == 2
        assert isinstance(conditional_branch_op.yielded_values[0], QoalaInteger)
        assert conditional_branch_op.yielded_values[0].value == 0
        assert isinstance(conditional_branch_op.yielded_values[1], QoalaInteger)
        assert conditional_branch_op.yielded_values[1].value == 0

        assert isinstance(main_block.operations[6], Add)
        add_op = main_block.operations[6]
        assert isinstance(add_op.operand_a, QoalaRuntimeValue)
        assert isinstance(add_op.operand_b, QoalaInteger)

    def test_using_local_quantum_value_from_branching(self):
        qubit = LocalQubit()
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
            with branch_false:
                cond_qubit.Y()
                branch_false.yield_value(cond_qubit)
        cond_qubit.H()
        meas = cond_qubit.measure()
        return_results(meas)

        main_block = QoalaProgram._instance.current_function()._main_block

        assert isinstance(main_block.operations[0], QoalaLocalQubit)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], QoalaInteger)
        assert isinstance(main_block.operations[3], LessThanOp)
        assert isinstance(main_block.operations[4], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[4].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[4].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[4]
        assert len(conditional_branch_op.yielded_values) == 2
        assert isinstance(conditional_branch_op.yielded_values[0], XGate)
        assert isinstance(conditional_branch_op.yielded_values[1], YGate)

        assert isinstance(main_block.operations[5], HGate)
        measure_op = main_block.operations[5]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)

        assert isinstance(main_block.operations[6], QubitMeasure)
        measure_op = main_block.operations[6]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)
        assert isinstance(main_block.operations[7], ReturnResultsOp)

        return_results_op = main_block.operations[7]
        assert len(return_results_op.values) == 1
        assert return_results_op.values[0] is main_block.operations[6]

    def test_using_entangled_quantum_value_from_branching(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        remote = Remote("Bob")
        qubit = Entangle("Bob")
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
            with branch_false:
                cond_qubit.Y()
                branch_false.yield_value(cond_qubit)
        cond_qubit.H()
        meas = cond_qubit.measure()
        return_results(meas)

        main_block = QoalaProgram._instance.current_function()._main_block

        assert isinstance(main_block.operations[0], QoalaEprs)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], QoalaInteger)
        assert isinstance(main_block.operations[3], LessThanOp)
        assert isinstance(main_block.operations[4], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[4].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[4].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[4]
        assert len(conditional_branch_op.yielded_values) == 2
        assert isinstance(conditional_branch_op.yielded_values[0], XGate)
        assert isinstance(conditional_branch_op.yielded_values[1], YGate)

        assert isinstance(main_block.operations[5], HGate)
        measure_op = main_block.operations[5]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)

        assert isinstance(main_block.operations[6], QubitMeasure)
        measure_op = main_block.operations[6]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)
        assert isinstance(main_block.operations[7], ReturnResultsOp)

        return_results_op = main_block.operations[7]
        assert len(return_results_op.values) == 1
        assert return_results_op.values[0] is main_block.operations[6]

        del QoalaProgram._declared_remotes
        del QoalaProgram._compilation_context

    def test_yield_classical_value_from_single_branch(self):
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            a = ScopedVar()
            with branch_true:
                a.assign(Int(15))
                branch_true.yield_value(a)
        b = a + 10

        main_block = QoalaProgram._instance.current_function()._main_block

        # Assert the types of ops of the main block:
        assert isinstance(main_block.operations[0], QoalaInteger)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], LessThanOp)
        assert isinstance(main_block.operations[3], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[3].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[3].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[3]
        assert len(conditional_branch_op.yielded_values) == 1
        assert isinstance(conditional_branch_op.yielded_values[0], QoalaInteger)
        assert conditional_branch_op.yielded_values[0].value == 15

        assert isinstance(main_block.operations[5], Add)
        add_op = main_block.operations[5]
        assert isinstance(add_op.operand_a, QoalaRuntimeValue)
        assert isinstance(add_op.operand_b, QoalaInteger)

    def test_yield_local_quantum_value_from_single_branch(self):
        qubit = LocalQubit()
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
        cond_qubit.H()
        meas = cond_qubit.measure()
        return_results(meas)

        main_block = QoalaProgram._instance.current_function()._main_block

        assert isinstance(main_block.operations[0], QoalaLocalQubit)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], QoalaInteger)
        assert isinstance(main_block.operations[3], LessThanOp)
        assert isinstance(main_block.operations[4], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[4].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[4].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[4]
        assert len(conditional_branch_op.yielded_values) == 1
        assert isinstance(conditional_branch_op.yielded_values[0], XGate)

        assert isinstance(main_block.operations[5], HGate)
        measure_op = main_block.operations[5]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)

        assert isinstance(main_block.operations[6], QubitMeasure)
        measure_op = main_block.operations[6]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)
        assert isinstance(main_block.operations[7], ReturnResultsOp)

        return_results_op = main_block.operations[7]
        assert len(return_results_op.values) == 1
        assert return_results_op.values[0] is main_block.operations[6]

    def test_yield_entangled_quantum_value_from_single_branch(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        remote = Remote("Bob")
        qubit = Entangle("Bob")
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
        cond_qubit.H()
        meas = cond_qubit.measure()
        return_results(meas)

        main_block = QoalaProgram._instance.current_function()._main_block

        assert isinstance(main_block.operations[0], QoalaEprs)
        assert isinstance(main_block.operations[1], QoalaInteger)
        assert isinstance(main_block.operations[2], QoalaInteger)
        assert isinstance(main_block.operations[3], LessThanOp)
        assert isinstance(main_block.operations[4], ConditionalBranching)
        # The conditional branching has 2 blocks:
        assert isinstance(main_block.operations[4].true_dest, QoalaBlock)
        assert isinstance(main_block.operations[4].false_dest, QoalaBlock)

        conditional_branch_op = main_block.operations[4]
        assert len(conditional_branch_op.yielded_values) == 1
        assert isinstance(conditional_branch_op.yielded_values[0], XGate)

        assert isinstance(main_block.operations[5], HGate)
        measure_op = main_block.operations[5]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)

        assert isinstance(main_block.operations[6], QubitMeasure)
        measure_op = main_block.operations[6]
        assert isinstance(measure_op.qubit, QoalaRuntimeQubit)
        assert isinstance(main_block.operations[7], ReturnResultsOp)

        return_results_op = main_block.operations[7]
        assert len(return_results_op.values) == 1
        assert return_results_op.values[0] is main_block.operations[6]

        del QoalaProgram._declared_remotes
        del QoalaProgram._compilation_context
