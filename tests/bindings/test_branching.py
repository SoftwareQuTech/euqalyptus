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
from qoala.types.classical import Int, ScopedVar
from qoala.types.quantum import LocalQubit, ScopedQubit
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


@QoalaProgram
def value_from_branching_single_branch_unsupported():
    with if_cond(Int(4) < 7) as (branch_true, branch_false):
        # Since there is a single branch, this example should just work
        # without using the ScopedVar programing protocol.
        # HOWEVER, we will still require it for harmonization purposes
        # and to simplify the construction of the AST
        with branch_true:
            a = Int(15)
    # This line should raise an exception *only* on compilation.
    # That's why this test case is not present on the syntax and AST tests.
    b = a + 10


@QoalaProgram
def value_from_branching_single_branch():
    with if_cond(Int(4) < 7) as (branch_true, branch_false):
        # Since there is a single branch, this example should just work
        # without using the ScopedVar programing protocol.
        # HOWEVER, we will still require it for harmonization purposes
        # and to simplify the construction of the AST
        a = ScopedVar()
        with branch_true:
            a.assign(Int(15))
            branch_true.yield_value(a)
    b = a + 10


@QoalaProgram
def classical_value_from_branching():
    with if_cond(Int(4) < 7) as (branch_true, branch_false):
        a = ScopedVar()  # Holds a classical value
        with branch_true:
            a.assign(Int(15))
            branch_true.yield_value(a)
        with branch_false:
            a.assign(Int(25))
            branch_false.yield_value(a)
    b = a + 10


@QoalaProgram
def qubit_value_from_branching():
    qubit = LocalQubit()  # Holds a qubit value
    with if_cond(Int(4) < 7) as (branch_true, branch_false):
        cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
        with branch_true:
            cond_qubit.X()
            branch_true.yield_value(cond_qubit)
        with branch_false:
            cond_qubit.Y()
            branch_false.yield_value(cond_qubit)
    res = cond_qubit.measure()

# TODO - Test a double nested if that returns a value from the inner-most level


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

    @pytest.mark.skip(reason="Not supported: It is not clear how to detect that a value was assigned "
                             "inside a branching instructions and used outside it")
    def test_value_from_branching_single_branch_unsupported(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = value_from_branching_single_branch_unsupported.module
        assert (
                str(ex.value)
                == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        # TODO - Update the error type risen!
        with pytest.raises(RuntimeError) as ex:
            _, _ = value_from_branching_single_branch_unsupported.compile()
        # TODO - assert the error message

    @pytest.mark.skip(reason="Not supported: Compiling single branches that yield values need "
                             "inserting a false branch that yields an unused value.")
    def test_value_from_branching_single_branch(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = value_from_branching_single_branch.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = value_from_branching_single_branch.compile()
        assert isinstance(module, QoalaModule)
        # WARNING - For the MLIR to be valid, scf.if *requires* a false branch when yielding values
        # This is a side effect of the fact that the value returned by the scf.if operation *must*
        # be clearly defined in both scenarios (true and false branch). This is needed *despite the
        # condition result is known at compile time*, since the scf dialect does not make any
        # assumption about the execution of the program. When lowering SCF to CF, some passes
        # applied *after* the lowering could use symbolic execution to discover the dead branch.
        expected_asm = """module {
  qnet.func @value_from_branching_single_branch() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi slt, %c4_i32, %c7_i32 : i32
    %1 = scf.if %0 -> (i32) {
      %c15_i32 = arith.constant 15 : i32
      scf.yield %c15_i32 : i32
    } else {
      %c0:i32 = arith.constant 0 : i32
      scf.yield %c0_i32 : i32
    }
    %c10_i32 = arith.constant 10 : i32
    %2 = arith.addi %1, %c10_i32 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm


    def test_classical_value_from_branching(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = classical_value_from_branching.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = classical_value_from_branching.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @classical_value_from_branching() {
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %0 = arith.cmpi slt, %c4_i32, %c7_i32 : i32
    %1 = scf.if %0 -> (i32) {
      %c15_i32 = arith.constant 15 : i32
      scf.yield %c15_i32 : i32
    } else {
      %c25_i32 = arith.constant 25 : i32
      scf.yield %c25_i32 : i32
    }
    %c10_i32 = arith.constant 10 : i32
    %2 = arith.addi %1, %c10_i32 : i32
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_qubit_value_from_branching(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = qubit_value_from_branching.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = qubit_value_from_branching.compile()
        assert isinstance(module, QoalaModule)
        # Note - MLIR does not offer a "boolean" type. values "true" and "false" are modeled as i1 values.
        expected_asm = """module {
  qnet.func @qubit_value_from_branching() {
    %0 = qnet.new_qubit : !qnet.qubit
    %c4_i32 = arith.constant 4 : i32
    %c7_i32 = arith.constant 7 : i32
    %1 = arith.cmpi slt, %c4_i32, %c7_i32 : i32
    %2 = scf.if %1 -> (!qnet.qubit) {
      %4 = qnet.x %0 : !qnet.qubit
      scf.yield %4 : !qnet.qubit
    } else {
      %4 = qnet.y %0 : !qnet.qubit
      scf.yield %4 : !qnet.qubit
    }
    %3 = qnet.measure %2 : i1
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
