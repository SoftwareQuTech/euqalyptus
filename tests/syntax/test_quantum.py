from qoala.types.classical.integer import Measure
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

    def test_qubit_operations(self):
        qubit = LocalQubit()

        qubit.X()
        qubit.Y()
        qubit.Z()
        qubit.T()
        qubit.H()
        qubit.K()
        qubit.S()

        assert isinstance(qubit, Qubit)
