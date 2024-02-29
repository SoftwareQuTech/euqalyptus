from typing import Generic, TypeVar

import pytest

from qoala.ast.value import QoalaExpression, QoalaInteger, QoalaFloat, QoalaArray
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float, Double, QoalaFloatingPointType
from qoala.types.classical.integer import Int32, UInt32, Int, QoalaIntegerType

_Base_Type_Int = TypeVar("_Base_Type_Int", bound=QoalaIntegerType)
_Base_Type_Float = TypeVar("_Base_Type_Float", bound=QoalaFloatingPointType)

"""
In these classes, we aim to test the syntax of the classical operations.
Being this said `we cannot test the results of the operations` since
computing the results will require executing the code.
To correctly check the usage of the syntax, we need to assert _the internal
state: of the objects returned by the program, so we check that the code
was "parsed" correctly.
"""


@pytest.mark.parametrize("clazz", (Int32, UInt32, Int))
class TestIntegerClassicalSyntax(Generic[_Base_Type_Int]):
    # These two methods are helpful to create the right type of integer, by
    # _statically_ calling the constructor depending on the name of the class.
    # It deviates a bit from what a user could write (a user will never use a
    # factory based on a parametric type), but it simplifies the specification
    # of all the possible test cases.

    @staticmethod
    def _get_int_from_immediate(clazz: type, immediate: int) -> _Base_Type_Int:
        match clazz.__name__:
            case "Int32":
                return Int32(immediate=immediate)
            case "UInt32":
                return UInt32(immediate=immediate)
            case "Int":
                return Int(immediate=immediate)
            case _:
                raise NotImplementedError()

    @staticmethod
    def _get_int_from_same_type(clazz: type, other_int: _Base_Type_Int) -> _Base_Type_Int:
        match clazz.__name__:
            case "Int32":
                return Int32(other=other_int)
            case "UInt32":
                return UInt32(other=other_int)
            case "Int":
                return Int(other=other_int)
            case _:
                raise NotImplementedError()

    def test_int_creation(self, clazz: type):
        value_a = TestIntegerClassicalSyntax._get_int_from_immediate(clazz, 0)
        assert isinstance(value_a, QoalaInteger)

    def test_int_creation_from_other_integer(self, clazz: type):
        value_a = TestIntegerClassicalSyntax._get_int_from_immediate(clazz, 10)
        value_b = TestIntegerClassicalSyntax._get_int_from_same_type(clazz, value_a)
        assert isinstance(value_b, QoalaInteger)

    def test_int_operator_overload_correctness(self, clazz: type):
        value_a = TestIntegerClassicalSyntax._get_int_from_immediate(clazz, 2)
        value_b = TestIntegerClassicalSyntax._get_int_from_immediate(clazz, 6)
        value_c = value_a + value_b
        value_d = value_b + value_a
        value_e = value_b - value_a
        value_f = value_a - value_b
        value_g = value_a * value_b
        value_h = value_b * value_a
        value_i = value_b / value_a
        value_j = value_a / value_b

        # Assert closure correctness
        assert isinstance(value_c, QoalaExpression)
        assert isinstance(value_d, QoalaExpression)
        assert isinstance(value_e, QoalaExpression)
        assert isinstance(value_f, QoalaExpression)
        assert isinstance(value_g, QoalaExpression)
        assert isinstance(value_h, QoalaExpression)
        assert isinstance(value_i, QoalaExpression)
        assert isinstance(value_j, QoalaExpression)


@pytest.mark.parametrize("clazz", (Float, Double))
class TestFloatClassicalSyntax(Generic[_Base_Type_Float]):
    @staticmethod
    def _get_float_from_immediate(clazz: type, immediate: float) -> _Base_Type_Float:
        match clazz.__name__:
            case "Float":
                return Float(immediate=immediate)
            case "Double":
                return Double(immediate=immediate)
            case _:
                raise NotImplementedError()

    @staticmethod
    def _get_float_from_same_type(clazz: type, other_int: _Base_Type_Float) -> _Base_Type_Float:
        match clazz.__name__:
            case "Float":
                return Float(other=other_int)
            case "Double":
                return Double(other=other_int)
            case _:
                raise NotImplementedError()

    def test_float_creation(self, clazz: type):
        value_a = TestFloatClassicalSyntax._get_float_from_immediate(clazz, 0)
        assert isinstance(value_a, QoalaFloat)

    def test_float_creation_from_other_int32(self, clazz: type):
        value_a = TestFloatClassicalSyntax._get_float_from_immediate(clazz, 10)
        value_b = TestFloatClassicalSyntax._get_float_from_same_type(clazz, value_a)
        assert isinstance(value_b, QoalaFloat)

    def test_float_operator_overload_correctness(self, clazz: type):
        value_a = TestFloatClassicalSyntax._get_float_from_immediate(clazz, 2)
        value_b = TestFloatClassicalSyntax._get_float_from_immediate(clazz, 6)
        value_c = value_a + value_b
        value_d = value_b + value_a
        value_e = value_b - value_a
        value_f = value_a - value_b
        value_g = value_a * value_b
        value_h = value_b * value_a
        value_i = value_b / value_a
        value_j = value_a / value_b

        # Assert closure correctness
        assert isinstance(value_c, QoalaExpression)
        assert isinstance(value_d, QoalaExpression)
        assert isinstance(value_e, QoalaExpression)
        assert isinstance(value_f, QoalaExpression)
        assert isinstance(value_g, QoalaExpression)
        assert isinstance(value_h, QoalaExpression)
        assert isinstance(value_i, QoalaExpression)
        assert isinstance(value_j, QoalaExpression)


class TestArrayClassicalSyntax:
    def test_declare_integer_array(self):
        val_a = Int(10)
        val_b = Int(20)
        int_array_a = IntArray()
        int_array_b = IntArray(val_a, val_b, 8)

        assert isinstance(int_array_a, QoalaArray)
        assert isinstance(int_array_b, QoalaArray)

    def test_store_in_integer_array(self):
        arr = IntArray()
        arr.store(Int(10))

        assert isinstance(arr, QoalaArray)

        value = arr[0]

        assert isinstance(value, QoalaExpression)

    def test_declare_float_array(self):
        val_a = Double(10.5)
        val_b = Double(20.1)
        int_array_a = FloatArray()
        int_array_b = FloatArray(val_a, val_b, 20.5)

        assert isinstance(int_array_a, QoalaArray)
        assert isinstance(int_array_b, QoalaArray)

    def test_store_in_float_array(self):
        arr = FloatArray()
        arr.store(Double(15.5))
        assert isinstance(arr, QoalaArray)

        value = arr[0]
        assert isinstance(value, QoalaExpression)
