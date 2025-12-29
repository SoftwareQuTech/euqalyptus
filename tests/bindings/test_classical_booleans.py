import pytest

from qoala import QoalaProgram, QoalaModule
from qoala.errors import NotYetCompiledError
from qoala.types.classical.booleans import Bool


@QoalaProgram
def simple_bool_program():
    bool_a = Bool(True)
    bool_b = Bool(False)


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