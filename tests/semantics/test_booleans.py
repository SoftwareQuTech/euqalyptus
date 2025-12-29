import pytest

import qoala.utils.debug_info as dbg_info
from qoala.ast.operations.boolean import And, Or, Xor
from qoala.ast.value import QoalaBool
from qoala.types.classical.booleans import Bool


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

    def test_basic_booleans(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        assert isinstance(bool_true, QoalaBool)
        assert bool_true.value == True
        assert isinstance(bool_false, QoalaBool)
        assert bool_false.value == False

    def test_boolean_arithmetic(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        bool_a = bool_true & bool_false
        bool_b = bool_true | bool_false
        bool_c = bool_true ^ bool_true

        assert isinstance(bool_a, And)
        assert isinstance(bool_b, Or)
        assert isinstance(bool_c, Xor)
