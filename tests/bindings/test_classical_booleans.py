import pytest

from euqalyptus import QoalaProgram, QoalaModule
from euqalyptus.errors import NotYetCompiledError
from euqalyptus.types.classical.booleans import Bool


@QoalaProgram
def simple_bool_program():
    bool_a = Bool(True)
    bool_b = Bool(False)


@QoalaProgram
def simple_bool_program_unary_ops():
    bool_true = Bool(True)
    bool_false = Bool(False)

    bool_a = -bool_true
    bool_b = ~bool_true


@QoalaProgram
def simple_bool_program_binary_ops():
    bool_true = Bool(True)
    bool_false = Bool(False)

    bool_a = bool_true & bool_false
    bool_b = bool_true | bool_false
    bool_c = bool_true ^ bool_true


@QoalaProgram
def simple_bool_program_binary_ops_with_immediates():
    bool_true = Bool(True)
    bool_false = Bool(False)

    # We test using an immediate both the left, and from the right
    bool_a = bool_true & True
    bool_b = False | bool_true
    bool_c = bool_true ^ True


@QoalaProgram
def complex_bool_condition():
    bool_true = Bool(True)
    bool_false = Bool(False)

    bool_res = ~(bool_true & ~(bool_false ^ bool_true))


class TestQoalaQnetPythonBindingsClassical:
    def test_simple_boolean_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_bool_program.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = simple_bool_program.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @simple_bool_program() {
    %true = arith.constant true
    %false = arith.constant false
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_simple_boolean_program_unary_ops_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_bool_program_unary_ops.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = simple_bool_program_unary_ops.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @simple_bool_program_unary_ops() {
    %true = arith.constant true
    %false = arith.constant false
    %true_0 = arith.constant true
    %0 = arith.xori %true, %true_0 : i1
    %true_1 = arith.constant true
    %1 = arith.xori %true, %true_1 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_simple_boolean_program_binary_ops_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_bool_program_binary_ops.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = simple_bool_program_binary_ops.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @simple_bool_program_binary_ops() {
    %true = arith.constant true
    %false = arith.constant false
    %0 = arith.andi %true, %false : i1
    %1 = arith.ori %true, %false : i1
    %2 = arith.xori %true, %true : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_simple_bool_program_binary_ops_with_immediates(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_bool_program_binary_ops_with_immediates.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = simple_bool_program_binary_ops_with_immediates.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @simple_bool_program_binary_ops_with_immediates() {
    %true = arith.constant true
    %false = arith.constant false
    %true_0 = arith.constant true
    %0 = arith.andi %true, %true_0 : i1
    %false_1 = arith.constant false
    %1 = arith.ori %true, %false_1 : i1
    %true_2 = arith.constant true
    %2 = arith.xori %true, %true_2 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_complex_bool_condition_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = complex_bool_condition.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = complex_bool_condition.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @complex_bool_condition() {
    %true = arith.constant true
    %false = arith.constant false
    %0 = arith.xori %false, %true : i1
    %true_0 = arith.constant true
    %1 = arith.xori %0, %true_0 : i1
    %2 = arith.andi %true, %1 : i1
    %true_1 = arith.constant true
    %3 = arith.xori %2, %true_1 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
