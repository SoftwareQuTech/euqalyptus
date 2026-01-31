import pytest

from qoala import QoalaProgram, QoalaModule
from qoala.errors import NotYetCompiledError
from qoala.operations import Remote
from qoala.operations.branching import if_cond
from qoala.operations.communication import (
    recv_int,
    recv_ints,
    recv_floats,
    send_floats,
    send_ints,
    recv_float,
)
from qoala.types.classical import IntArray, FloatArray, Int
from qoala.types.quantum import Entangle, LocalQubit


@QoalaProgram
def classical_remote_communication():
    remote = Remote("Bob")
    ints = recv_ints(remote, 10)
    int_b = ints[0] + ints[5]


@QoalaProgram
def classical_send_immediate_values():
    remote = Remote("Alice")
    send_ints("Alice", 10, 20)
    send_floats(remote, 3.14, 2.71)


@QoalaProgram
def classical_send_measurement_values_as_int():
    remote = Remote("Alice")
    qubit = LocalQubit()
    measurement = qubit.measure()
    send_ints(remote, measurement)


@QoalaProgram
def classical_send_measurement_values_as_float():
    remote = Remote("Alice")
    qubit = LocalQubit()
    measurement = qubit.measure()
    send_floats(remote, measurement)


@QoalaProgram
def classical_send_array_of_values():
    remote = Remote("Alice")
    # We're not interested on testing how an array can be created from values and immediates
    # For that, see the corresponding test on the "test_classical_floats_ints.py" file
    int_vals = IntArray(10, 20)
    float_vals = FloatArray(3.14, 2.71)
    send_ints("Alice", int_vals)
    send_floats(remote, float_vals)


@QoalaProgram
def classical_send_immediates_and_array_of_values():
    remote = Remote("Alice")
    # We're not interested on testing how an array can be created from values and immediates
    # For that, see the corresponding test on the "test_classical_floats_ints.py" file
    int_vals = IntArray(10, 20)
    float_vals = FloatArray(3.14, 2.71)
    send_ints("Alice", int_vals, 30)
    send_floats(remote, float_vals, 15.65)


@QoalaProgram
def quantum_entanglement_program():
    Remote("Bob")
    q = Entangle("Bob")
    t1 = recv_int("Bob")
    q.rot_X(t1)
    t2 = recv_int("Bob")
    q.rot_Y(t2)
    m = q.measure()


@QoalaProgram
def quantum_entanglement_program_c():
    Remote("Bob")
    q = Entangle("Bob", 3)
    t1 = recv_floats("Bob", 2)
    # We access the entangled qubits as if they were an array
    q[2].rot_X(angle=t1[0])
    q[2].rot_Y(angle=t1[1])
    m = q[2].measure()
    t2 = recv_ints("Bob", 5)
    # Here we try to use an index whose value is only known at runtime
    # We DO NOT support this yet
    q[t2[4]].H()


@QoalaProgram
def program_using_recv_int_for_comparison():
    Remote("Alice")
    qubit = Entangle("Alice")
    local_qubit = LocalQubit()
    x = recv_int("Alice")

    with if_cond(x == 0) as (branch_true, branch_false):
        with branch_true:
            qubit.X()
        with branch_false:
            local_qubit.Z()

    val = Int(10)


@QoalaProgram
def program_using_recv_float_for_comparison():
    Remote("Alice")
    qubit = Entangle("Alice")
    local_qubit = LocalQubit()
    x = recv_float("Alice")

    with if_cond(x == 0.0) as (branch_true, branch_false):
        with branch_true:
            qubit.X()
        with branch_false:
            local_qubit.Z()

    val = Int(10)


class TestQoalaQnetPythonBindingsQuantum:
    def test_classical_remote_communication(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_remote_communication.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_remote_communication.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.remote @Bob
  qnet.func @classical_remote_communication() {
    %0 = qnet.recv_ints  {length = 10 : i32, remote = @Bob} : tensor<10xi32>
    %c0 = arith.constant 0 : index
    %extracted = tensor.extract %0[%c0] : tensor<10xi32>
    %c5 = arith.constant 5 : index
    %extracted_0 = tensor.extract %0[%c5] : tensor<10xi32>
    %1 = arith.addi %extracted, %extracted_0 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_send_immediate_values(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_send_immediate_values.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_send_immediate_values.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @classical_send_immediate_values() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %from_elements = tensor.from_elements %c10_i32, %c20_i32 : tensor<2xi32>
    qnet.send_ints %from_elements {remote = @Alice} : tensor<2xi32>
    %cst = arith.constant 3.140000e+00 : f32
    %cst_0 = arith.constant 2.710000e+00 : f32
    %from_elements_1 = tensor.from_elements %cst, %cst_0 : tensor<2xf32>
    qnet.send_floats %from_elements_1 {remote = @Alice} : tensor<2xf32>
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_classical_send_measurement_as_int(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_send_measurement_values_as_int.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_send_measurement_values_as_int.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @classical_send_measurement_values_as_int() {
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.measure %0 : i1
    %2 = arith.extui %1 : i1 to i32
    %from_elements = tensor.from_elements %2 : tensor<1xi32>
    qnet.send_ints %from_elements {remote = @Alice} : tensor<1xi32>
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_classical_send_measurement_as_float(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_send_measurement_values_as_float.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_send_measurement_values_as_float.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @classical_send_measurement_values_as_float() {
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.measure %0 : i1
    %2 = arith.extui %1 : i1 to i32
    %3 = arith.uitofp %2 : i32 to f32
    %from_elements = tensor.from_elements %3 : tensor<1xf32>
    qnet.send_floats %from_elements {remote = @Alice} : tensor<1xf32>
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_classical_send_array_of_values(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_send_array_of_values.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_send_array_of_values.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @classical_send_array_of_values() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %from_elements = tensor.from_elements %c10_i32, %c20_i32 : tensor<2xi32>
    %cst = arith.constant 3.140000e+00 : f32
    %cst_0 = arith.constant 2.710000e+00 : f32
    %from_elements_1 = tensor.from_elements %cst, %cst_0 : tensor<2xf32>
    %from_elements_2 = tensor.from_elements %c10_i32, %c20_i32 : tensor<2xi32>
    qnet.send_ints %from_elements_2 {remote = @Alice} : tensor<2xi32>
    %from_elements_3 = tensor.from_elements %cst, %cst_0 : tensor<2xf32>
    qnet.send_floats %from_elements_3 {remote = @Alice} : tensor<2xf32>
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_classical_send_immediates_and_array_of_values(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_send_immediates_and_array_of_values.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_send_immediates_and_array_of_values.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @classical_send_immediates_and_array_of_values() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %from_elements = tensor.from_elements %c10_i32, %c20_i32 : tensor<2xi32>
    %cst = arith.constant 3.140000e+00 : f32
    %cst_0 = arith.constant 2.710000e+00 : f32
    %from_elements_1 = tensor.from_elements %cst, %cst_0 : tensor<2xf32>
    %c30_i32 = arith.constant 30 : i32
    %from_elements_2 = tensor.from_elements %c10_i32, %c20_i32, %c30_i32 : tensor<3xi32>
    qnet.send_ints %from_elements_2 {remote = @Alice} : tensor<3xi32>
    %cst_3 = arith.constant 1.565000e+01 : f32
    %from_elements_4 = tensor.from_elements %cst, %cst_0, %cst_3 : tensor<3xf32>
    qnet.send_floats %from_elements_4 {remote = @Alice} : tensor<3xf32>
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_entanglement_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_entanglement_program.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
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
  qnet.remote @Bob
  qnet.func @quantum_entanglement_program() {
    %0 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %1 = qnet.recv_int  {remote = @Bob} : i32
    %c0_i32 = arith.constant 0 : i32
    %2 = qnet.rot_x_int %0, %1, %c0_i32 : !qnet.qubit
    %3 = qnet.recv_int  {remote = @Bob} : i32
    %c0_i32_0 = arith.constant 0 : i32
    %4 = qnet.rot_y_int %2, %3, %c0_i32_0 : !qnet.qubit
    %5 = qnet.measure %4 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    @pytest.mark.skip(
        reason="Not supported: Using multiple entangled qubits using array syntax is not supported yet"
    )
    def test_entanglement_program_c_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_entanglement_program_c.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = quantum_entanglement_program_c.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.remote @Bob
  qnet.func @quantum_entanglement_program_c() {
    %0 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %1 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %2 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %from_elements = tensor.from_elements %0, %1, %2 : tensor<3x!qnet.qubit>
    %3 = qnet.recv_floats  {length = 2 : i32, remote = @Bob} : tensor<2xf32>
    %c2 = arith.constant 2 : index
    %extracted = tensor.extract %from_elements[%c2] : tensor<3x!qnet.qubit>
    %c0 = arith.constant 0 : index
    %extracted_0 = tensor.extract %3[%c0] : tensor<2xf32>
    %4 = qnet.rot_x %extracted, %extracted_0 : !qnet.qubit
    %c2_1 = arith.constant 2 : index
    %extracted_2 = tensor.extract %from_elements[%c2_1] : tensor<3x!qnet.qubit>
    %c1 = arith.constant 1 : index
    %extracted_3 = tensor.extract %3[%c1] : tensor<2xf32>
    %5 = qnet.rot_y %extracted_2, %extracted_3 : !qnet.qubit
    %c2_4 = arith.constant 2 : index
    %extracted_5 = tensor.extract %from_elements[%c2_4] : tensor<3x!qnet.qubit>
    %6 = qnet.measure %extracted_5 : i1
    %7 = qnet.recv_ints  {length = 2 : i32, remote = @Bob} : tensor<5xi32>
    %c4 = arith.constant 4 : index
    %extracted_6 = tensor.extract %7[%c4] : tensor<5xi32>
    %8 = arith.index_cast %extracted_6 : i32 to index
    %extracted_7 = tensor.extract %from_elements[%8] : tensor<3x!qnet.qubit>
    %9 = qnet.hadamard %extracted_7 : !qnet.qubit
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_using_recv_int_as_comparison_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = program_using_recv_int_for_comparison.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = program_using_recv_int_for_comparison.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @program_using_recv_int_for_comparison() {
    %0 = qnet.eprs  {remote = @Alice} : !qnet.qubit
    %1 = qnet.new_qubit : !qnet.qubit
    %2 = qnet.recv_int  {remote = @Alice} : i32
    %c0_i32 = arith.constant 0 : i32
    %3 = arith.cmpi eq, %2, %c0_i32 : i32
    scf.if %3 {
      %4 = qnet.x %0 : !qnet.qubit
    } else {
      %4 = qnet.z %1 : !qnet.qubit
    }
    %c10_i32 = arith.constant 10 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_using_recv_float_as_comparison_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = program_using_recv_float_for_comparison.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = program_using_recv_float_for_comparison.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.remote @Alice
  qnet.func @program_using_recv_float_for_comparison() {
    %0 = qnet.eprs  {remote = @Alice} : !qnet.qubit
    %1 = qnet.new_qubit : !qnet.qubit
    %2 = qnet.recv_float  {remote = @Alice} : f32
    %cst = arith.constant 0.000000e+00 : f32
    %3 = arith.cmpf oeq, %2, %cst : f32
    scf.if %3 {
      %4 = qnet.x %0 : !qnet.qubit
    } else {
      %4 = qnet.z %1 : !qnet.qubit
    }
    %c10_i32 = arith.constant 10 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
