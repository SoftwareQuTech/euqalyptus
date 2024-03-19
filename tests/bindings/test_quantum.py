import pytest

from qoala import QoalaProgram, QoalaModule, NotYetCompiledError
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.quantum.qubit import LocalQubit


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
    # qubit.cphase(qubit_b)

    measurement = qubit.measure()


class TestQoalaHIRPythonBindingsQuantum:
    def test_complex_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = complex_quantum_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = complex_quantum_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  func.func @complex_quantum_program() {
    %c20_i32 = arith.constant 20 : i32
    %c30_i32 = arith.constant 30 : i32
    %cst = arith.constant 2.120000e+01 : f32
    %0 = hir.new_qubit : !hir.qubit
    %1 = hir.new_qubit : !hir.qubit
    %c10_i32 = arith.constant 10 : i32
    %c30_i32_0 = arith.constant 30 : i32
    %cst_1 = arith.constant 0.000000e+00 : f32
    %2 = hir.rot_x %0, %cst_1 : !hir.qubit
    %c10_i32_2 = arith.constant 10 : i32
    %cst_3 = arith.constant 1.050000e+01 : f32
    %3 = hir.rot_y %0, %cst_3 : !hir.qubit
    %4 = hir.rot_z %0, %cst : !hir.qubit
    %qout0, %qout1 = hir.cnot %0, %1 : !hir.qubit, !hir.qubit
    %5 = hir.measure %qout0 : i1
    return
  }
}
"""
        assert str(module.asm) == expected_asm
