import pytest

from qoala import QoalaExpression, QoalaProgram, CompilationContext
from qoala.ast.model import QoalaBlock
from qoala.ast.operations.branching import ConditionalBranching
from qoala.operations import Remote
from qoala.operations.branching import (
    if_cond,
    if_eq,
    if_neq,
    if_lt,
    if_le,
    if_gt,
    if_ge,
)
from qoala.operations.control_flow import return_results
from qoala.types.classical import Int, ScopedVar
from qoala.types.classical.booleans import Bool
from qoala.types.quantum import LocalQubit, ScopedQubit
from qoala.types.quantum.qubit import Entangle
from qoala.utils import debug_info as dbg_info
from tests.helpers_tests import DummyQoalaProgram


class TestBooleanSyntax:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info on initialization
        dbg_info.function_name = "setup_debug_info"
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            getattr(request.cls, request.node.originalname)
        )
        QoalaProgram._instance._module.add_function(request.node.name)
        # We now set the real function name, so we can obtain meaningful dbg info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name
        yield
        QoalaProgram._instance._module.remove_function(request.node.name)
        del QoalaProgram._instance

    def test_direct_boolean_creation(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        assert isinstance(bool_true, QoalaExpression)
        assert isinstance(bool_false, QoalaExpression)

    def test_boolean_operations(self):
        bool_true = Bool(True)
        bool_false = Bool(False)

        bool_a = bool_true & bool_false
        bool_b = bool_true | bool_false
        bool_c = bool_true ^ bool_true
        bool_d = -bool_true
        bool_e = ~bool_true

        assert isinstance(bool_a, QoalaExpression)
        assert isinstance(bool_b, QoalaExpression)
        assert isinstance(bool_c, QoalaExpression)
        assert isinstance(bool_d, QoalaExpression)
        assert isinstance(bool_e, QoalaExpression)


class TestBranchingSyntax:
    @pytest.fixture(autouse=True, scope="function")
    def setup_debug_info(self, request):
        # For allowing debug info on initialization
        dbg_info.function_name = "setup_debug_info"
        # For testing purposes, we manually create a dummy program and attach a function to it.
        # With this hack, we can assert the structure of the generated program
        QoalaProgram._instance = DummyQoalaProgram(
            getattr(request.cls, request.node.originalname)
        )
        QoalaProgram._instance._module.add_function(request.node.name)
        # We now set the real function name, so we can obtain meaningful dbg info
        # Nuance; parametrized tests use [param-types]... remove that part
        if "[" in request.node.name:
            bracket_index = request.node.name.index("[")
            dbg_info.function_name = request.node.name[0:bracket_index]
        else:
            dbg_info.function_name = request.node.name
        yield
        QoalaProgram._instance._module.remove_function(request.node.name)
        del QoalaProgram._instance

    def test_branching_simple_if(self):
        bool_true = Bool(True)
        branching = if_cond(bool_true)
        assert isinstance(branching, ConditionalBranching)
        with if_cond(Int(4) < 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_branching_equals(self):
        branching = if_eq(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        with if_eq(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_branching_not_equals(self):
        branching = if_neq(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        with if_neq(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_branching_less_than(self):
        branching = if_lt(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        with if_lt(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_branching_less_than_or_equals(self):
        branching = if_le(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        with if_le(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_branching_greater_than(self):
        branching = if_gt(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        with if_gt(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_branching_greater_than_or_equals(self):
        branching = if_ge(Int(4), 10)
        assert isinstance(branching, ConditionalBranching)
        with if_ge(Int(4), 10) as (branch_true, branch_false):
            with branch_true:
                assert isinstance(branch_true, QoalaBlock)
                a = Int(10)
            with branch_false:
                assert isinstance(branch_false, QoalaBlock)
                a = Int(20)
        b = a + 10

    def test_using_classical_value_from_branching(self):
        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            a = ScopedVar()  # Holds a classical value
            with branch_true:
                a.assign(Int(15))
                branch_true.yield_value(a)
            with branch_false:
                a.assign(Int(25))
                branch_false.yield_value(a)
        b = a + 10

    def test_capture_classical_value_in_scoped_var(self):
        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        old_val = Int(0)
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            a = ScopedVar(old_val)  # Holds a classical value
            with branch_true:
                branch_true.yield_value(a)
            with branch_false:
                branch_false.yield_value(a)
        b = a + 10

    def test_using_local_quantum_value_from_branching(self):
        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        qubit = LocalQubit()  # Holds a qubit value
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
            with branch_false:
                cond_qubit.Y()
                branch_false.yield_value(cond_qubit)
        meas = cond_qubit.measure()
        return_results(meas)

    def test_using_entangled_quantum_value_from_branching(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        remote = Remote("Bob")
        qubit = Entangle("Bob")  # Holds a qubit value
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
            with branch_false:
                cond_qubit.Y()
                branch_false.yield_value(cond_qubit)
        meas = cond_qubit.measure()
        return_results(meas)

        del QoalaProgram._declared_remotes
        del QoalaProgram._compilation_context

    def test_yield_classical_value_from_single_branch(self):
        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        qubit = LocalQubit()  # Holds a qubit value
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
        meas = cond_qubit.measure()
        return_results(meas)

    def test_yield_local_quantum_value_from_single_branch(self):
        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        qubit = LocalQubit()  # Holds a qubit value
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
        meas = cond_qubit.measure()
        return_results(meas)

    def test_yield_entangled_quantum_value_from_single_branch(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        # Since this is a syntax test, we only need to make sure that the
        # types and method invocations do not raise exceptions.
        remote = Remote("Bob")
        qubit = Entangle("Bob")  # Holds a qubit value
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            cond_qubit = ScopedQubit(qubit)  # Holds a qubit value
            with branch_true:
                cond_qubit.X()
                branch_true.yield_value(cond_qubit)
        meas = cond_qubit.measure()
        return_results(meas)

    def test_update_scoped_vals_values(self):
        # Using the "counter = counter + 1" is a chicken-and-egg problem.
        # Tradeoff: If we "update" the variable "counter"
        #  counter = counter + 1
        # Then we are implicitly *replacing* the old value in the variable "counter" (a ScopedVar object)
        # with whatever is the result of "counter + 1" (an "Add" object).
        # This leads to loosing all the chain of operations applied on the counter.
        # Then, when we yield the value, we are yielding the last operation object and not the ScopedVal.
        # Let's now consider the following statement:
        #  counter = counter + 1
        # * The left side if a variable name "counter"
        # * The right side performs a "+" operation, with two operands: an immediate "1" and
        #   a reference to the value in the scope named "counter".
        # * The "=" performs an assignation. Since the left side of the assignation is a name that
        #   _is already defined in the scope_, then the semantics of the assignation will *overwrite* the
        #   current value in scope stored under the name "scope".
        # Considering this, I explored the possibility to allow directly yielding the final operation
        # of all the chain applied over a ScopedValue. At the end, this led to "simply" assigning the
        # operation object that is being created (in this case, an "Add" operation) to the ScopedVar object.
        # However, when we're creating the "Add" object, we're processing the _right side_ of the assignation,
        # so we cannot assume that one of the operands is the value being overwritten.
        # The "solution" to this problem is, again, to "hook" the assignation operation, which we
        # already deemed unfeasible for this time being.
        init = Int(0)
        with if_cond(Int(4) < 7) as (branch_true, branch_false):
            counter = ScopedVar(init)  # Holds a qubit value
            with branch_true:
                aux = counter + 1
                # Rewriting the helper value _is allowed_... as long as we assign the
                # las updated value to the ScopedVar object.
                aux = aux * 2
                # We assign to the ScopedVar the *last* value
                # The critical operation is the *assignation*, which *needs to capture
                # the last value* that need to be yielded outside the branch.
                counter.assign(aux)
                branch_true.yield_value(counter)
        result = counter * 10
        return_results(result)
