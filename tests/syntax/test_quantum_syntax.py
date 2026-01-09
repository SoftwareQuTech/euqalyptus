import pytest

import qoala.utils.debug_info as dbg_info
from qoala import QoalaProgram
from qoala.ast.operations.quantum import QubitMeasure
from qoala.ast.qubit import QoalaQubit
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.quantum.qubit import LocalQubit
from tests.helpers_tests import DummyQoalaProgram


class TestQuantumSyntax:

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

    def test_qubit_allocation(self):
        qubit = LocalQubit()

        assert isinstance(qubit, QoalaQubit)

    def test_qubit_measurement(self):
        qubit = LocalQubit()

        measurement = qubit.measure()

        assert isinstance(qubit, QoalaQubit)
        assert isinstance(measurement, QubitMeasure)

    def test_qubit_operations_with_no_args(self):
        qubit = LocalQubit()

        qubit.X()
        qubit.Y()
        qubit.Z()
        qubit.T()
        qubit.H()
        qubit.S()

        measurement = qubit.measure()

        assert isinstance(qubit, QoalaQubit)

        assert isinstance(measurement, QubitMeasure)

    def test_qubit_operations_with_args(self):
        n_val = Int(20)
        d_val = Int(30)
        angle_val = Float(21.2)

        qubit = LocalQubit()
        qubit_b = LocalQubit()

        # Arguments for the operations can be either a "python" immediate
        # or a qoala value. In the former case, the rotation will immediately
        # create a qoala immediate to store the value.
        qubit.rot_X(n=10, d=30)
        qubit.rot_Y(n=10, d=d_val, angle=10.5)
        qubit.rot_Z(n=n_val, d=d_val, angle=angle_val)

        qubit.cnot(qubit_b)
        qubit.cphase(qubit_b)

        measurement = qubit.measure()

        assert isinstance(qubit, QoalaQubit)
        assert isinstance(measurement, QubitMeasure)
