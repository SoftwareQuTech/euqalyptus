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


@QoalaProgram
def simple_if():
    with if_cond(Int(4) < 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_equals():
    with if_eq(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_not_equals():
    with if_neq(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_less_than():
    with if_lt(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_less_than_or_equals():
    with if_le(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_greater_than():
    with if_gt(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_greater_than_or_equals():
    with if_ge(Int(4), 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(15)
        with branch_false:
            a = Int(25)
    b = Int(30) + 10


@QoalaProgram
def branching_not_using_false_branch():
    with if_cond(Int(4) == 7) as (branch_true, branch_false):
        with branch_true:
            a = Int(25)
        # We deliberately don't have a "branch_false" (not used)
    b = Int(15) + 10


@QoalaProgram
def branching_not_using_true_branch():
    with if_cond(Int(4) == 7) as (branch_true, branch_false):
        with branch_false:
            a = Int(25)
            assert len(branch_false.operations) == 1
    b = Int(15) + 10


@QoalaProgram
def branching_nested():
    with if_cond(Int(4) == 7) as (branch_true_l1, _):
        with branch_true_l1:
            with if_cond(Int(5) <= 10) as (branch_true_l2, _):
                with branch_true_l2:
                    a = Int(25)
    b = Int(15) + 10


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
        expected_asm = """module {
  qnet.func @simple_if() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi slt, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
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
        expected_asm = """module {
  qnet.func @branching_equals() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi eq, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
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
        expected_asm = """module {
  qnet.func @branching_not_equals() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi ne, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
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
        expected_asm = """module {
  qnet.func @branching_less_than() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi slt, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
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
        expected_asm = """module {
  qnet.func @branching_less_than_or_equals() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi sle, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
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
        expected_asm = """module {
  qnet.func @branching_greater_than() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi sgt, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
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
        expected_asm = """module {
  qnet.func @branching_greater_than_or_equals() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi sge, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c15_i32 = arith.constant 15 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
    }
    %c30_i32 = arith.constant 30 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c30_i32, %c10_i32 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_branching_missing_false_branch(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_not_using_false_branch.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_not_using_false_branch.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @branching_not_using_false_branch() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi eq, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c25_i32 = arith.constant 25 : i32
    }
    %c15_i32 = arith.constant 15 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c15_i32, %c10_i32 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    @pytest.mark.skip(reason="Missing true branch is not supported yet")
    def test_branching_missing_true_branch(self):
        # TODO - To fully support missing the true branch, we need to negate the condition
        #  and place the old false branch in the true branch with the negated condition.
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_not_using_true_branch.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_not_using_true_branch.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @branching_not_using_true_branch() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi eq, %c4_i32, %c7_i32 : i32
    cf.cond_br %0, ^bb2, ^bb1
  ^bb1:  // pred: ^bb0
    %c25_i32 = arith.constant 25 : i32
    cf.br ^bb2
  ^bb2:  // 2 preds: ^bb0, ^bb1
    %c15_i32 = arith.constant 15 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c15_i32, %c10_i32 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_nested_branching_instructions(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = branching_nested.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = branching_nested.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @branching_nested() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi eq, %c4_i32, %c7_i32 : i32
    scf.if %0 {
      %c5_i32 = arith.constant 5 : i32
      %c10_i32_0 = arith.constant 10 : i32
      %2 = arith.cmpi sle, %c5_i32, %c10_i32_0 : i32
      scf.if %2 {
        %c25_i32 = arith.constant 25 : i32
      }
    }
    %c15_i32 = arith.constant 15 : i32
    %c10_i32 = arith.constant 10 : i32
    %1 = arith.addi %c15_i32, %c10_i32 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
