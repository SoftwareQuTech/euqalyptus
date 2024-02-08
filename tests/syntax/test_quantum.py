from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Measure, Int
from qoala.types.quantum.qubit import Qubit, LocalQubit


class TestQuantumSyntax:
    def test_qubit_allocation(self):
        qubit = LocalQubit()

        assert isinstance(qubit, Qubit)

    def test_qubit_measurement(self):
        qubit = LocalQubit()

        measurement = qubit.measure()

        assert isinstance(qubit, Qubit)
        assert isinstance(measurement, Measure)

    def test_qubit_operations_with_no_args(self):
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

        assert isinstance(qubit, Qubit)

        assert isinstance(measurement, Measure)

    def test_qubit_operations_with_args(self):
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

        assert isinstance(qubit, Qubit)
        assert isinstance(measurement, Measure)

