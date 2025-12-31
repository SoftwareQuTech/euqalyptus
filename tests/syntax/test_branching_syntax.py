import pytest

import qoala.utils.debug_info as dbg_info
from qoala import QoalaExpression
from qoala.ast.model import BlockPlaceholder
from qoala.ast.operations.branching import BranchingOp
from qoala.operations.branching import if_cond, if_eq, if_neq, if_lt, if_le, if_gt, if_ge
from qoala.types.classical import Int
from qoala.types.classical.booleans import Bool


class TestBooleanSyntax:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name

    def test_direct_boolean_creation(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        assert isinstance(bool_true, QoalaExpression)
        assert isinstance(bool_false, QoalaExpression)

    def test_boolean_operations(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        bool_a = bool_true & bool_false
        bool_b = bool_true | bool_false
        bool_c = bool_true ^ bool_true
        bool_d = -bool_true
        bool_e = ~bool_true

        assert isinstance(bool_a, QoalaExpression)
        assert isinstance(bool_b, QoalaExpression)
        assert isinstance(bool_c, QoalaExpression)
        assert isinstance(bool_d, QoalaExpression)
        assert isinstance(bool_e, QoalaExpression)


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
        assert isinstance(branching, BranchingOp)
        with if_cond(Int(4) < 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10

    def test_branching_equals(self):
        branching = if_eq(Int(4), 10)
        assert isinstance(branching, BranchingOp)
        with if_eq(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10

    def test_branching_not_equals(self):
        branching = if_neq(Int(4), 10)
        assert isinstance(branching, BranchingOp)
        with if_neq(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10

    def test_branching_less_than(self):
        branching = if_lt(Int(4), 10)
        assert isinstance(branching, BranchingOp)
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
        assert isinstance(branching, BranchingOp)
        with if_le(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10

    def test_branching_greater_than(self):
        branching = if_gt(Int(4), 10)
        assert isinstance(branching, BranchingOp)
        with if_gt(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10

    def test_branching_greater_than_or_equals(self):
        branching = if_ge(Int(4), 10)
        assert isinstance(branching, BranchingOp)
        with if_ge(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, BlockPlaceholder)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, BlockPlaceholder)
                a = Int(20)
        b = a + 10
