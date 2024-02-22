from qoala.ast.qubit import QoalaLocalQubit
from qoala.types.quantum.qubit import LocalQubit


class TestQuantumSemantics:
    def test_basic_quantum_semantics(self):
        qubit = LocalQubit()

        assert isinstance(qubit, QoalaLocalQubit)
        # TODO - Assert the internal status of the allocated qubit
