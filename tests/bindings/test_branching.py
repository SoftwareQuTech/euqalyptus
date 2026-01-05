import pytest

from qoala import QoalaProgram, NotYetCompiledError, QoalaModule
from qoala.operations.branching import (
    if_cond,
    if_eq,
    if_neq,
    if_lt,
    if_le,
    if_gt,
    if_ge,
)
from qoala.types.classical import Int
from qoala.utils import debug_info as dbg_info


class DummyQoalaProgram(QoalaProgram):
    pass


@QoalaProgram
def simple_if():
    with if_cond(Int(4) < 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = a + 10


@QoalaProgram
def branching_equals():
    with if_eq(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = a + 10


@QoalaProgram
def branching_not_equals():
    with if_neq(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = a + 10


@QoalaProgram
def branching_less_than():
    with if_lt(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = a + 10


@QoalaProgram
def branching_less_than_or_equals():
    with if_le(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(15)
    b = a + 10


@QoalaProgram
def branching_greater_than():
    with if_gt(Int(4), 10) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(15)
    b = a + 10


@QoalaProgram
def branching_greater_than_or_equals():
    with if_ge(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(15)
    b = a + 10


class TestBranchingInstructionsBindings:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name

    def test_branching_simple_if(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_if.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = simple_if.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @simple_if() {
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

    def test_branching_equals(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_equals.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_equals.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @branching_equals() {
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

    def test_branching_not_equals(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_not_equals.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_not_equals.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @branching_not_equals() {
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

    def test_branching_less_than(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_less_than.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_less_than.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @branching_less_than() {
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

    def test_branching_less_than_or_equals(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_less_than_or_equals.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_less_than_or_equals.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @branching_less_than_or_equals() {
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

    def test_branching_greater_than(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_greater_than.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_greater_than.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @branching_greater_than() {
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

    def test_branching_greater_than_or_equals(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_greater_than_or_equals.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_greater_than_or_equals.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        # TODO - adjust the expected output
        expected_asm = """module {
  qnet.func @branching_greater_than_or_equals() {
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
