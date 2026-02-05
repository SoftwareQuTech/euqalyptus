import pytest

from euqalyptus import QoalaProgram, QoalaModule
from euqalyptus.errors import NotYetCompiledError
from euqalyptus.types.classical import Float, Int
from euqalyptus.types.quantum import LocalQubit


@QoalaProgram
def quantum_base_gates_program():
    n_val = Int(20)
    d_val = Int(30)
    angle_val = Float(21.2)

    qubit = LocalQubit()
    qubit_b = LocalQubit()

    qubit.rot_X(n=10, d=2)
    qubit.rot_Y(n=10, d=d_val, angle=10.5)
    qubit.rot_Z(n=n_val, d=d_val, angle=angle_val)

    qubit.cnot(qubit_b)

    measurement_a = qubit.measure()
    measurement_b = qubit_b.measure()


@QoalaProgram
def quantum_base_gates_program_b():

    qubit = LocalQubit()

    qubit.rot_X(n=2, d=3)
    qubit.rot_Y(n=1, d=0)

    measurement_a = qubit.measure()


@QoalaProgram
def quantum_alias_gates_program():
    qubit = LocalQubit()
    qubit_b = LocalQubit()

    qubit.X()
    qubit.Y()
    qubit.Z()
    qubit.S()
    qubit.T()
    qubit.cphase(qubit_b)

    qubit.measure()
    qubit_b.measure()


class TestQoalaQnetPythonBindingsQuantum:

    def test_base_gates_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_base_gates_program.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = quantum_base_gates_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @quantum_base_gates_program() {
    %c20_i32 = arith.constant 20 : i32
    %c30_i32 = arith.constant 30 : i32
    %cst = arith.constant 2.120000e+01 : f32
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.new_qubit : !qnet.qubit
    %c10_i32 = arith.constant 10 : i32
    %c2_i32 = arith.constant 2 : i32
    %2 = qnet.rot_x_int %0, %c10_i32, %c2_i32 : !qnet.qubit
    %cst_0 = arith.constant 1.050000e+01 : f32
    %3 = qnet.rot_y %2, %cst_0 : !qnet.qubit
    %4 = qnet.rot_z %3, %cst : !qnet.qubit
    %qout0, %qout1 = qnet.cnot %4, %1 : !qnet.qubit, !qnet.qubit
    %5 = qnet.measure %qout0 : i1
    %6 = qnet.measure %qout1 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_base_gates_program_to_qoala_qnet_b(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_base_gates_program_b.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = quantum_base_gates_program_b.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @quantum_base_gates_program_b() {
    %0 = qnet.new_qubit : !qnet.qubit
    %c2_i32 = arith.constant 2 : i32
    %c3_i32 = arith.constant 3 : i32
    %1 = qnet.rot_x_int %0, %c2_i32, %c3_i32 : !qnet.qubit
    %c1_i32 = arith.constant 1 : i32
    %c0_i32 = arith.constant 0 : i32
    %2 = qnet.rot_y_int %1, %c1_i32, %c0_i32 : !qnet.qubit
    %3 = qnet.measure %2 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_alias_gates_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_alias_gates_program.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = quantum_alias_gates_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @quantum_alias_gates_program() {
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.new_qubit : !qnet.qubit
    %2 = qnet.x %0 : !qnet.qubit
    %3 = qnet.y %2 : !qnet.qubit
    %4 = qnet.z %3 : !qnet.qubit
    %cst = arith.constant 1.57079637 : f32
    %5 = qnet.rot_z %4, %cst : !qnet.qubit
    %cst_0 = arith.constant 0.785398185 : f32
    %6 = qnet.rot_z %5, %cst_0 : !qnet.qubit
    %qout0, %qout1 = qnet.cz %6, %1 : !qnet.qubit, !qnet.qubit
    %7 = qnet.measure %qout0 : i1
    %8 = qnet.measure %qout1 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
