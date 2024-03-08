import pytest

from qoala import QoalaProgram, QoalaModule, NotYetCompiledError
from qoala.types.classical.integer import Int
from qoala.types.classical.floats import Float
from qoala.types.quantum.qubit import LocalQubit


@QoalaProgram
def empty_program():
    pass


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

    @pytest.mark.skip(reason="Generation of QoalaHIRof simple operations not supported yet")
    def test_simple_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """"builtin.module"() ({
  "func.func"() <{function_type = (none) -> none, sym_name = "simple_arith_program"}> ({
    # TODO
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
