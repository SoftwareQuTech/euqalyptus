import pytest

from qoala import QoalaProgram, QoalaModule, NotYetCompiledError
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.quantum.qubit import LocalQubit, Entangle
from qoala.operations.quantum import recv_int, recv_floats


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
    # CPhase gates cannot be compiled yet
    # qubit.cphase(qubit_b)

    measurement_a = qubit.measure()
    measurement_b = qubit_b.measure()


@QoalaProgram
def quantum_entanglement_program():
    q = Entangle("Bob", 1)[0]
    t1 = recv_int("Bob")
    q.rot_X(t1)
    t2 = recv_int("Bob")
    q.rot_Y(t2)
    m = q.measure()


@QoalaProgram
def quantum_entanglement_program_b():
    q = Entangle("Bob", 3)[2]
    t1 = recv_floats("Bob", 2)
    q.rot_X(angle=t1[0])
    t2 = recv_floats("Bob", 2)
    q.rot_Y(angle=t2[1])
    m = q.measure()


class TestQoalaQnetPythonBindingsQuantum:
    def test_complex_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = complex_quantum_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = complex_quantum_program.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.func @complex_quantum_program() {
    %c20_i32 = arith.constant 20 : i32
    %c30_i32 = arith.constant 30 : i32
    %cst = arith.constant 2.120000e+01 : f32
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.new_qubit : !qnet.qubit
    %cst_0 = arith.constant 0.0306796152 : f32
    %2 = qnet.rot_x %0, %cst_0 : !qnet.qubit
    %cst_1 = arith.constant 1.050000e+01 : f32
    %3 = qnet.rot_y %2, %cst_1 : !qnet.qubit
    %4 = qnet.rot_z %3, %cst : !qnet.qubit
    %qout0, %qout1 = qnet.cnot %4, %1 : !qnet.qubit, !qnet.qubit
    %5 = qnet.measure %qout0 : i1
    %6 = qnet.measure %qout1 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_entanglement_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_entanglement_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = quantum_entanglement_program.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.func @quantum_entanglement_program() {
    qnet.remote @Bob
    %0 = qnet.eprs  {N = 1 : i32, remote = @Bob} : tensor<1x!qnet.qubit>
    %c0 = arith.constant 0 : index
    %extracted = tensor.extract %0[%c0] : tensor<1x!qnet.qubit>
    %1 = qnet.recv_ints  {remote = @Bob} : tensor<1xi32>
    %c0_0 = arith.constant 0 : index
    %extracted_1 = tensor.extract %1[%c0_0] : tensor<1xi32>
    %cst = arith.constant 0.000000e+00 : f32
    %cst_2 = arith.constant 3.14159274 : f32
    %2 = arith.uitofp %extracted_1 : i32 to f32
    %3 = arith.mulf %2, %cst_2 : f32
    %4 = math.exp2 %cst : f32
    %5 = arith.divf %3, %4 : f32
    %6 = qnet.rot_x %extracted, %5 : !qnet.qubit
    %7 = qnet.recv_ints  {remote = @Bob} : tensor<1xi32>
    %c0_3 = arith.constant 0 : index
    %extracted_4 = tensor.extract %7[%c0_3] : tensor<1xi32>
    %cst_5 = arith.constant 0.000000e+00 : f32
    %cst_6 = arith.constant 3.14159274 : f32
    %8 = arith.uitofp %extracted_4 : i32 to f32
    %9 = arith.mulf %8, %cst_6 : f32
    %10 = math.exp2 %cst_5 : f32
    %11 = arith.divf %9, %10 : f32
    %12 = qnet.rot_y %6, %11 : !qnet.qubit
    %13 = qnet.measure %12 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_entanglement_program_b_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_entanglement_program_b.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = quantum_entanglement_program_b.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.func @quantum_entanglement_program_b() {
    qnet.remote @Bob
    %0 = qnet.eprs  {N = 3 : i32, remote = @Bob} : tensor<3x!qnet.qubit>
    %c2 = arith.constant 2 : index
    %extracted = tensor.extract %0[%c2] : tensor<3x!qnet.qubit>
    %1 = qnet.recv_floats  {remote = @Bob} : tensor<2xf32>
    %c0 = arith.constant 0 : index
    %extracted_0 = tensor.extract %1[%c0] : tensor<2xf32>
    %2 = qnet.rot_x %extracted, %extracted_0 : !qnet.qubit
    %3 = qnet.recv_floats  {remote = @Bob} : tensor<2xf32>
    %c1 = arith.constant 1 : index
    %extracted_1 = tensor.extract %3[%c1] : tensor<2xf32>
    %4 = qnet.rot_y %2, %extracted_1 : !qnet.qubit
    %5 = qnet.measure %4 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
