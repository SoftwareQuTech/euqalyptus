import pytest

from qoala import QoalaProgram, QoalaModule, NotYetCompiledError
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.quantum.qubit import LocalQubit


@QoalaProgram
def empty_program():
    pass


@QoalaProgram
def simple_arith_program():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b

    float_a = Float(10.0)
    float_b = Float(20.0)

    float_c = float_a - float_b

    int_d = 10 * int_c
    int_e = int_d / 5

    float_d = float_c * 20.0
    float_e = float_d / 4.0


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
    def test_empty_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = empty_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = empty_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  func.func @empty_program() {
    return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_simple_integer_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  func.func @simple_arith_program() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %0 = arith.addi %c10_i32, %c20_i32 : i32
    %cst = arith.constant 1.000000e+01 : f32
    %cst_0 = arith.constant 2.000000e+01 : f32
    %1 = arith.addf %cst, %cst_0 : f32
    return
  }
}
"""
        assert str(module.asm) == expected_asm

    @pytest.mark.skip(reason="Generation of QoalaHIR of complex operations not supported yet")
    def test_complex_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = complex_quantum_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = complex_quantum_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """"builtin.module"() ({
  "func.func"() <{function_type = (none) -> none, sym_name = "simple_arith_program"}> ({
    # TODO
  }) : () -> ()
}) : () -> ()
"""
        assert str(module.asm) == expected_asm
