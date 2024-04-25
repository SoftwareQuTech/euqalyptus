import pytest

import qoala.utils.debug_info as dbg_info
from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.value import QoalaInteger, QoalaFloat, Signedness
from qoala.errors import InvalidArrayArgumentError, NotUnsignedIntegerArgumentError, NotIntegerArgumentError
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int32, UInt32


class TestNumbersSemantics:
    numeric_test_data = [
        (10, 20, Int32, QoalaInteger),
        (11.1, 22.2, Float, QoalaFloat)
    ]

    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name

    @pytest.mark.parametrize("val_a, val_b, numeric_type, internal_type", numeric_test_data)
    def test_basic_numeric_semantics(
            self,
            val_a: int | float,
            val_b: int | float,
            numeric_type: Int32 | Float,
            internal_type: QoalaInteger | QoalaFloat,
    ):
        int_a = numeric_type(val_a)
        int_b = numeric_type(val_b)
        int_c = int_a + int_b
        int_d = int_a - int_b
        int_e = int_a * int_b
        int_f = int_a / int_b

        # From the syntax tests, we know that all the statements above
        # return a QoalaExpression. We now want to test for the specific
        # type and the content within it
        assert isinstance(int_a, internal_type)
        assert isinstance(int_b, internal_type)
        assert isinstance(int_c, Add)
        assert isinstance(int_d, Subtract)
        assert isinstance(int_e, Multiply)
        assert isinstance(int_f, Divide)

        assert int_a.width == 32
        if numeric_type == Int32:
            assert int_a.signedness == Signedness.SIGNED
        elif numeric_type == Float:
            assert int_a.signedness == Signedness.UNKNOWN
        else:
            pytest.fail("Unknown numeric type")
        assert int_a.value == val_a

        assert int_b.width == 32
        if numeric_type == Int32:
            assert int_a.signedness == Signedness.SIGNED
        elif numeric_type == Float:
            assert int_a.signedness == Signedness.UNKNOWN
        else:
            pytest.fail("Unknown numeric base type")
        assert int_b.value == val_b

        assert int_c.operand_a is int_a
        assert int_c.operand_b is int_b

        assert int_d.operand_a is int_a
        assert int_d.operand_b is int_b

        assert int_e.operand_a is int_a
        assert int_e.operand_b is int_b

        assert int_f.operand_a is int_a
        assert int_f.operand_b is int_b

    def test_wrong_numeric_initialization(self):
        with pytest.raises(NotUnsignedIntegerArgumentError) as ex:
            _ = UInt32(-10)
        assert str(ex.value) == "'UInt32' type only supports positive integer values"

        with pytest.raises(NotIntegerArgumentError) as ex:
            _ = Int32(10.2)
        assert str(ex.value) == "'Int32' type only supports integer values"

        with pytest.raises(NotIntegerArgumentError) as ex:
            _ = UInt32(0.25)
        assert str(ex.value) == "'UInt32' type only supports integer values"

        with pytest.raises(NotIntegerArgumentError) as ex:
            _ = UInt32(-3.25)
        assert str(ex.value) == "'UInt32' type only supports integer values"

    def test_wrong_array_initialization(self):
        with pytest.raises(InvalidArrayArgumentError) as ex:
            _ = IntArray(10.2)
        assert str(ex.value) == "Array of type 'IntArray' can only hold values of type 'int'"
        with pytest.raises(InvalidArrayArgumentError) as ex:
            _ = FloatArray(10)
        assert str(ex.value) == "Array of type 'FloatArray' can only hold values of type 'float'"
