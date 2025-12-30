import pytest

import qoala.utils.debug_info as dbg_info
from qoala import QoalaExpression
from qoala.operations.branching import if_eq
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

    def test_branching_equals(self):
        # TODO - Complement this test with asserts and the type of the "branch blocks"
        bool_true = Bool(True)
        with if_eq(bool_true) as (branch_true, branch_false):
            with branch_true:
                a = Int(10)
            with branch_false:
                a = Int(20)
        b = a + 10
