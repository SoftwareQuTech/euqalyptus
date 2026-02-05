from typing import Generic, TypeVar

import pytest

import euqalyptus.utils.debug_info as dbg_info
from euqalyptus import QoalaProgram
from euqalyptus.ast.value import (
    QoalaExpression,
    QoalaInteger,
    QoalaFloat,
    QoalaArray,
)
from euqalyptus.types.classical.arrays import IntArray, FloatArray
from euqalyptus.types.classical.floats import Float, Double, QoalaFloatingPointType
from euqalyptus.types.classical.integer import Int32, UInt32, Int, QoalaIntegerType
from tests.helpers_tests import DummyQoalaProgram

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

    @staticmethod
    def _get_int_from_immediate(clazz: type, immediate: int) -> _Base_Type_Int:
        match clazz.__name__:
            case "Int32":
                return Int32(immediate=immediate)  # type: ignore[no-any-return]
            case "UInt32":
                return UInt32(immediate=immediate)  # type: ignore[no-any-return]
            case "Int":
                return Int(immediate=immediate)  # type: ignore[no-any-return]
            case _:
                raise NotImplementedError()

    @staticmethod
    def _get_int_from_same_type(
        clazz: type, other_int: _Base_Type_Int
    ) -> _Base_Type_Int:
        match clazz.__name__:
            case "Int32":
                return Int32(other=other_int)  # type: ignore[no-any-return]
            case "UInt32":
                return UInt32(other=other_int)  # type: ignore[no-any-return]
            case "Int":
                return Int(other=other_int)  # type: ignore[no-any-return]
            case _:
                raise NotImplementedError()

    def test_int_creation(self, clazz: type):
        value_a: _Base_Type_Int = TestIntegerClassicalSyntax._get_int_from_immediate(
            clazz, 0
        )
        assert isinstance(value_a, QoalaInteger)

    def test_int_creation_from_other_integer(self, clazz: type):
        value_a: _Base_Type_Int = TestIntegerClassicalSyntax._get_int_from_immediate(
            clazz, 10
        )
        value_b: _Base_Type_Int = TestIntegerClassicalSyntax._get_int_from_same_type(
            clazz, value_a
        )
        assert isinstance(value_b, QoalaInteger)

    def test_int_operator_overload_correctness(self, clazz: type):
        value_a: _Base_Type_Int = TestIntegerClassicalSyntax._get_int_from_immediate(
            clazz, 2
        )
        value_b: _Base_Type_Int = TestIntegerClassicalSyntax._get_int_from_immediate(
            clazz, 6
        )
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

    @staticmethod
    def _get_float_from_immediate(clazz: type, immediate: float) -> _Base_Type_Float:
        match clazz.__name__:
            case "Float":
                return Float(immediate=immediate)  # type: ignore[no-any-return]
            case "Double":
                return Double(immediate=immediate)  # type: ignore[no-any-return]
            case _:
                raise NotImplementedError()

    @staticmethod
    def _get_float_from_same_type(
        clazz: type, other_int: _Base_Type_Float
    ) -> _Base_Type_Float:
        match clazz.__name__:
            case "Float":
                return Float(other=other_int)  # type: ignore[no-any-return]
            case "Double":
                return Double(other=other_int)  # type: ignore[no-any-return]
            case _:
                raise NotImplementedError()

    def test_float_creation(self, clazz: type):
        value_a: _Base_Type_Float = TestFloatClassicalSyntax._get_float_from_immediate(
            clazz, 0
        )
        assert isinstance(value_a, QoalaFloat)

    def test_float_creation_from_other_int32(self, clazz: type):
        value_a: _Base_Type_Float = TestFloatClassicalSyntax._get_float_from_immediate(
            clazz, 10
        )
        value_b: _Base_Type_Float = TestFloatClassicalSyntax._get_float_from_same_type(
            clazz, value_a
        )
        assert isinstance(value_b, QoalaFloat)

    def test_float_operator_overload_correctness(self, clazz: type):
        value_a: _Base_Type_Float = TestFloatClassicalSyntax._get_float_from_immediate(
            clazz, 2
        )
        value_b: _Base_Type_Float = TestFloatClassicalSyntax._get_float_from_immediate(
            clazz, 6
        )
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

    def test_order_operations_no_immediate(self):
        result_a = Int(10) < Int(20)
        result_b = Int(10) <= Int(20)
        result_c = Int(10) > Int(20)
        result_d = Int(10) >= Int(20)
        result_e = Int(10) == Int(20)

        assert isinstance(result_a, QoalaExpression)
        assert isinstance(result_b, QoalaExpression)
        assert isinstance(result_c, QoalaExpression)
        assert isinstance(result_d, QoalaExpression)
        assert isinstance(result_e, QoalaExpression)

    def test_order_operations_immediate_right(self):
        result_a = Int(10) < 20
        result_b = Int(10) <= 20
        result_c = Int(10) > 20
        result_d = Int(10) >= 20
        result_e = Int(10) == 20

        assert isinstance(result_a, QoalaExpression)
        assert isinstance(result_b, QoalaExpression)
        assert isinstance(result_c, QoalaExpression)
        assert isinstance(result_d, QoalaExpression)
        assert isinstance(result_e, QoalaExpression)

    def test_order_operations_immediate_left(self):
        result_a = 10 < Int(20)
        result_b = 10 <= Int(20)
        result_c = 10 > Int(20)
        result_d = 10 >= Int(20)
        result_e = 10 == Int(20)

        assert isinstance(result_a, QoalaExpression)
        assert isinstance(result_b, QoalaExpression)
        assert isinstance(result_c, QoalaExpression)
        assert isinstance(result_d, QoalaExpression)
        assert isinstance(result_e, QoalaExpression)

    def test_order_operations_mixed_types(self):
        result_a = Float(10) < Int(20)
        result_b = Float(10) <= Int(20)
        result_c = Float(10) > Int(20)
        result_d = Float(10) >= Int(20)
        result_e = Float(10) == Int(20)

        assert isinstance(result_a, QoalaExpression)
        assert isinstance(result_b, QoalaExpression)
        assert isinstance(result_c, QoalaExpression)
        assert isinstance(result_d, QoalaExpression)
        assert isinstance(result_e, QoalaExpression)
