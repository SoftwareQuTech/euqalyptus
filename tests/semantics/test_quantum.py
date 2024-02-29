import pytest

from qoala.ast.qubit import QoalaLocalQubit
from qoala.ast.value import QoalaBit
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.quantum.qubit import LocalQubit


@pytest.mark.skip(reason="Rethink if these tests make sense or not; it seems that it is not\n"
                         "possible to assert more than what it is asserted here, which is\n"
                         "pretty much what we can assert about syntax.")
class TestQuantumSemantics:
    def test_basic_quantum_semantics(self):
        qubit = LocalQubit()

        assert isinstance(qubit, QoalaLocalQubit)
        # TODO - Assert the internal status of the allocated qubit

    def test_qubit_measurement_semantics(self):
        qubit = LocalQubit()

        measurement = qubit.measure()

        assert isinstance(qubit, QoalaLocalQubit)
        assert isinstance(measurement, QoalaBit)
        # TODO - Assert the internal status of the allocated qubit and measurement result

    def test_qubit_operations_with_no_args_semantics(self):
        qubit = LocalQubit()

        qubit.X()
        qubit.Y()
        qubit.Z()
        qubit.T()
        qubit.H()
        qubit.K()
        qubit.S()

        measurement = qubit.measure()
        qubit.reset()

        assert isinstance(qubit, QoalaLocalQubit)
        assert isinstance(measurement, QoalaBit)
        # TODO - Assert the internal status of the allocated qubit and measurement result

    def test_qubit_operations_with_args_semantics(self):
        n_val = Int(20)
        d_val = Int(30)
        angle_val = Float(21.2)

        qubit = LocalQubit()
        qubit_b = LocalQubit()

        # Arguments for the operations can be either a "python" immediate
        # or a qoala value. In the former case, the rotation will immediately
        # create a qoala immediate to store the value.
        qubit.rot_X(
            n=10,
            d=30
        )
        qubit.rot_Y(
            n=10,
            d=d_val,
            angle=10.5
        )
        qubit.rot_Z(
            n=n_val,
            d=d_val,
            angle=angle_val
        )

        qubit.cnot(qubit_b)
        qubit.cphase(qubit_b)

        measurement = qubit.measure()

        assert isinstance(qubit, QoalaLocalQubit)
        assert isinstance(qubit_b, QoalaLocalQubit)
        assert isinstance(measurement, QoalaBit)
        # TODO - Assert the internal status of the allocated qubit and measurement result
