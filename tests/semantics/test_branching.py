import pytest

import qoala.utils.debug_info as dbg_info
from qoala.ast.model import BlockPlaceholder
from qoala.ast.operations.branching import ConditionalBranching
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


class TestBranchingSyntax:
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
        bool_true = Bool(True)
        branching = if_cond(bool_true)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, QoalaBool)
        assert branching.condition.value == True

        with if_cond(Int(4) < 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
                assert len(branch_false.operations) == 1
        b = a + 10

    def test_branching_equals(self):
        branching = if_eq(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, EqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 10

        with if_eq(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
                assert len(branch_false.operations) == 1
        b = a + 10

    def test_branching_not_equals(self):
        branching = if_neq(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, NotEqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 10

        with if_neq(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
                assert len(branch_false.operations) == 1
        b = a + 10

    def test_branching_less_than(self):
        branching = if_lt(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, LessThanOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 10

        with if_lt(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10

    def test_branching_less_than_or_equals(self):
        branching = if_le(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, LessThanOrEqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 10

        with if_le(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
                assert len(branch_false.operations) == 1

    def test_branching_greater_than(self):
        branching = if_gt(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, GreaterThanOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 10

        with if_gt(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
                assert len(branch_false.operations) == 1
        b = a + 10

    def test_branching_greater_than_or_equals(self):
        branching = if_ge(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        assert isinstance(branching.condition, GreaterThanOrEqualsOp)
        assert isinstance(branching.condition.operand_a, QoalaInteger)
        assert branching.condition.operand_a.value == 4
        assert isinstance(branching.condition.operand_b, QoalaInteger)
        assert branching.condition.operand_b.value == 10

        with if_ge(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
                assert len(branch_true.operations) == 1
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
                assert len(branch_false.operations) == 1
        b = a + 10
