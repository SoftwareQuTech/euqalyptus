import pytest

import qoala.utils.debug_info as dbg_info
from qoala import QoalaProgram
from qoala.ast.operations.boolean import AndOp, OrOp, XorOp, NotOp
from qoala.ast.value import QoalaBool
from qoala.types.classical.booleans import Bool
from tests.helpers_tests import DummyQoalaProgram


class TestNumbersSemantics:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            getattr(request.cls, request.node.originalname)
        )
        QoalaProgram._instance._module.add_function(request.node.name)
        yield
        QoalaProgram._instance._module.remove_function(request.node.name)
        del QoalaProgram._instance

    def test_basic_booleans(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        assert isinstance(bool_true, QoalaBool)
        assert bool_true.value == True
        assert isinstance(bool_false, QoalaBool)
        assert bool_false.value == False

    def test_boolean_operations(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        bool_a = bool_true & bool_false
        bool_b = bool_true | bool_false
        bool_c = bool_true ^ bool_true
        bool_d = -bool_true
        bool_e = ~bool_true

        assert isinstance(bool_a, AndOp)
        assert isinstance(bool_a.operand_a, QoalaBool)
        assert bool_a.operand_a.value == True
        assert isinstance(bool_a.operand_b, QoalaBool)
        assert bool_a.operand_b.value == False

        assert isinstance(bool_b, OrOp)
        assert isinstance(bool_b.operand_a, QoalaBool)
        assert bool_b.operand_a.value == True
        assert isinstance(bool_b.operand_b, QoalaBool)
        assert bool_b.operand_b.value == False

        assert isinstance(bool_c, XorOp)
        assert isinstance(bool_c.operand_a, QoalaBool)
        assert bool_c.operand_a.value == True
        assert isinstance(bool_c.operand_b, QoalaBool)
        assert bool_c.operand_b.value == True

        assert isinstance(bool_d, NotOp)
        assert isinstance(bool_d.operand, QoalaBool)
        assert bool_d.operand.value == True

        assert isinstance(bool_e, NotOp)
        assert isinstance(bool_e.operand, QoalaBool)
        assert bool_e.operand.value == True
