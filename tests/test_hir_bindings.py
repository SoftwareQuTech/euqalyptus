import pytest

from qoala import QoalaProgram, NotYetCompiledError
from qoala.types.classical.integer import Int
from qoala.types.classical.floats import Float
from qoala.types.quantum.qubit import LocalQubit


@QoalaProgram
def simple_arith_program():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b


@QoalaProgram
def complex_quantum_program():
    n_val = Int(20)
    d_val = Int(30)
    angle_val = Float(21.2)

    qubit = LocalQubit()
    qubit_b = LocalQubit()

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


class TestQoalaHIRPythonBindings:
    def test_simple_program_to_qoala_HIR(self):
        with pytest.raises(NotYetCompiledError) as ex:
            module = simple_arith_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"

    def test_complex_progra_to_qoala_HIR(self):
        pass
