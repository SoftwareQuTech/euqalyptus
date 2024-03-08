import pytest

from qoala import QoalaProgram, QoalaModule, NotYetCompiledError
from qoala.types.classical.integer import Int
from qoala.types.classical.floats import Float
from qoala.types.quantum.qubit import LocalQubit


@QoalaProgram
def empty_program():
    pass


@QoalaProgram
def simple_arith_program_with_int():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b


@QoalaProgram
def simple_arith_program_with_floats():
    # Despite that it is supported, if we pass an integer (like "10") as the immediate
    # we will trigger a SIGSEGV in the mlir bindings library
    # TODO- Investigate this issue!
    int_a = Float(10.0)
    int_b = Float(20.0)

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
    def test_empty_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = empty_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = empty_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """"builtin.module"() ({
  "func.func"() <{function_type = (none) -> none, sym_name = "empty_program"}> ({
  ^bb0:
  }) : () -> ()
}) : () -> ()
"""
        assert str(module.asm) == expected_asm

    def test_simple_integer_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program_with_int.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program_with_int.compile()
        assert isinstance(module, QoalaModule)
        # Note - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #        (the signedness) to create the builtin type using IntegerType.get_(un)signed(width).
        #        Since we request a _signed_ integer type, then we will end up with a "si32" type in the
        #        generated intermediate representation.
        expected_asm = """"builtin.module"() ({
  "func.func"() <{function_type = (none) -> none, sym_name = "simple_arith_program_with_int"}> ({
    %0 = "arith.constant"() <{value = 10 : si32}> : () -> si32
    %1 = "arith.constant"() <{value = 20 : si32}> : () -> si32
    %2 = "arith.addi"(%0, %1) : (si32, si32) -> si32
  }) : () -> ()
}) : () -> ()
"""
        assert str(module.asm) == expected_asm

    def test_simple_float_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program_with_floats.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program_with_floats.compile()
        assert isinstance(module, QoalaModule)
        # NOTE: For some reason we get the "fastmath" attribute in the "arith.addf" operation
        #       In the meantime, we will simply let it be there, but it will be nice to get rid of it
        expected_asm = """"builtin.module"() ({
  "func.func"() <{function_type = (none) -> none, sym_name = "simple_arith_program_with_floats"}> ({
    %0 = "arith.constant"() <{value = 1.000000e+01 : f32}> : () -> f32
    %1 = "arith.constant"() <{value = 2.000000e+01 : f32}> : () -> f32
    %2 = "arith.addf"(%0, %1) <{fastmath = #arith.fastmath<none>}> : (f32, f32) -> f32
  }) : () -> ()
}) : () -> ()
"""
        assert str(module.asm) == expected_asm

    @pytest.mark.skip(reason="Generation of QoalaHIRof comples operations not supported yet")
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
