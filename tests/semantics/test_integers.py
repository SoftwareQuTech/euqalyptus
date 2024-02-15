from typing import Union

import pytest

from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.value import QoalaInteger, QoalaFloat, Signedness
from qoala.types.classical import InvalidArgumentError
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int32, UInt32


class TestIntegerSemantics:
    numeric_test_data = [
        (10, 20, Int32, QoalaInteger),
        (11.1, 22.2, Float, QoalaFloat)
    ]

    @pytest.mark.parametrize("val_a, val_b, numeric_type, internal_type", numeric_test_data)
    def test_basic_numeric_semantics(
            self,
            val_a: Union[int, float],
            val_b: Union[int, float],
            numeric_type: Union[Int32, Float],
            internal_type: Union[QoalaInteger, QoalaFloat],
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
            pytest.fail("Unknown numeric type")
        assert int_b.value == val_b

        assert int_c.operand_a == int_a
        assert int_c.operand_b == int_b

        assert int_d.operand_a == int_a
        assert int_d.operand_b == int_b

        assert int_e.operand_a == int_a
        assert int_e.operand_b == int_b

        assert int_f.operand_a == int_a
        assert int_f.operand_b == int_b

    def test_wrong_numeric_initialization(self):
        with pytest.raises(InvalidArgumentError) as ex:
            _ = UInt32(-10)
        assert str(ex.value) == "'UInt32' type only supports positive integer values"

        with pytest.raises(InvalidArgumentError) as ex:
            _ = Int32(10.2)
        assert str(ex.value) == "'Int32' type only supports integer values"

        with pytest.raises(InvalidArgumentError) as ex:
            _ = UInt32(0.25)
        assert str(ex.value) == "'UInt32' type only supports integer values"

        with pytest.raises(InvalidArgumentError) as ex:
            _ = UInt32(-3.25)
        assert str(ex.value) == "'UInt32' type only supports integer values"

    arrays_test_data = [
        ((10, 20), (5, 3), Int32, IntArray),
        ((15.3, 10), (-5.8, 4.1), Float, FloatArray)
    ]
