from queue import Queue
from typing import Type, Tuple, Union, List

import pytest

import qoala.utils.debug_info as dbg_info
from tests.helpers_tests import DummyQoalaProgram
from qoala import QoalaProgram
from qoala.ast.value import QoalaArray, QoalaInteger, QoalaFloat
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int32

class TestArraySemantics:
    arrays_test_data = [
        ((10, 20), (5, 3), int, Int32, IntArray, QoalaInteger),
        ((15.3, 10), (-5.8, 4.1), float, Float, FloatArray, QoalaFloat),
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
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(getattr(request.cls, request.node.originalname))
        QoalaProgram._instance._module.add_function(request.node.name)
        yield
        QoalaProgram._instance._module.remove_function(request.node.name)
        del QoalaProgram._instance

    @pytest.mark.parametrize(
        "values, constants, vals_type, base_type, array_type, member_type",
        arrays_test_data,
    )
    def test_array_semantics(
        self,
        values: Union[Tuple[int], Tuple[float]],
        constants: Union[Tuple[int], Tuple[float]],
        vals_type: Type,
        base_type: Type,
        array_type: Type,
        member_type: QoalaInteger | QoalaFloat,
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
