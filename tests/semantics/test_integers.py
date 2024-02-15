from queue import Queue
from typing import Union, Tuple, Type, List

import pytest

from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.value import QoalaInteger, QoalaFloat, Signedness, QoalaArray
from qoala.types.classical import InvalidArgumentError
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int32, UInt32


class TestNumbersSemantics:
    numeric_test_data = [
        (10, 20, Int32, QoalaInteger),
        (11.1, 22.2, Float, QoalaFloat)
    ]

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


class TestArraySemantics:
    arrays_test_data = [
        ((10, 20), (5, 3), int, Int32, IntArray, QoalaInteger),
        ((15.3, 10), (-5.8, 4.1), float, Float, FloatArray, QoalaFloat)
    ]

    @pytest.mark.parametrize("values, constants, vals_type, base_type, array_type, member_type", arrays_test_data)
    def test_array_semantics(
            self,
            values: Union[Tuple[int], Tuple[float]],
            constants: Union[Tuple[int], Tuple[float]],
            vals_type: Type,
            base_type: Type,
            array_type: Type,
            member_type: Union[QoalaInteger, QoalaFloat]
    ):
        array_values: List[member_type, vals_type] = []
        in_order_values: Queue[vals_type] = Queue()
        for value in values:
            array_values.append(base_type(value))
            in_order_values.put(value)

        for constant in constants:
            array_values.append(constant)
            in_order_values.put(constant)

        array = array_type(*array_values)

        assert isinstance(array, QoalaArray)
        assert array.length == 4
        assert array.base_size == 32
        assert array.base_type == vals_type

        for member in array.members:
            assert isinstance(member, member_type)

            # We assert the _order_ of the values on the list
            current_expected_value = in_order_values.get()
            # An AssertError on this line means that the build of the array
            # is not correct
            assert member.value == current_expected_value

            # We don't need to assert the internals of each member, since that
            # is covered by other tests in this file
