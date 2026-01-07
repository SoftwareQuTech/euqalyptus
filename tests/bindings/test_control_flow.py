import pytest

from qoala import QoalaProgram, QoalaModule
from qoala.errors import NotYetCompiledError
from qoala.operations.control_flow import return_results
from qoala.types.classical import Int, Float
from qoala.types.quantum import LocalQubit


@QoalaProgram
def return_empty():
    return_results()


@QoalaProgram
def return_measurement_result():
    q = LocalQubit()
    m = q.measure()
    return_results(m)


@QoalaProgram
def return_int():
    two = Int(2)
    return_results(two)


@QoalaProgram
def return_float():
    pi = Float(3.14)
    return_results(pi)


@QoalaProgram
def return_bool():
    a = Int(1)
    b = Int(2)

    check = a == b

    return_results(check)


@QoalaProgram
def return_mixed():
    q = LocalQubit()
    m = q.measure()

    two = Int(2)

    pi = Float(3.14)

    return_results(m, two, pi)


class TestQoalaQnetPythonBindingsControlFlow:
    def test_return_empty(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = return_empty.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = return_empty.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @return_empty() {
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_return_measurement_result(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = return_measurement_result.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = return_measurement_result.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @return_measurement_result() {
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.measure %0 : i1
    qnet.return %1 : i1
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_return_int(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = return_int.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = return_int.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @return_int() {
    %c2_i32 = arith.constant 2 : i32
    qnet.return %c2_i32 : i32
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_return_float(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = return_float.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = return_float.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @return_float() {
    %cst = arith.constant 3.140000e+00 : f32
    qnet.return %cst : f32
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_return_bool(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = return_bool.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = return_bool.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @return_bool() {
    %c1_i32 = arith.constant 1 : i32
    %c2_i32 = arith.constant 2 : i32
    %0 = arith.cmpi eq, %c1_i32, %c2_i32 : i32
    %1 = arith.cmpi eq, %c1_i32, %c2_i32 : i32
    qnet.return %1 : i1
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_return_mixed(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = return_mixed.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = return_mixed.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @return_mixed() {
    %0 = qnet.new_qubit : !qnet.qubit
    %1 = qnet.measure %0 : i1
    %c2_i32 = arith.constant 2 : i32
    %cst = arith.constant 3.140000e+00 : f32
    qnet.return %1, %c2_i32, %cst : i1, i32, f32
  }
}
"""
        assert str(module.asm) == expected_asm
