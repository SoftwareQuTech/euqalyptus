import pytest

import qoala.utils.debug_info as dbg_info
from qoala import QoalaProgram, CompilationContext
from qoala.ast.operations.branching import ConditionalBranching
from qoala.ast.operations.casts import IntToFloat, BitToInt
from qoala.ast.operations.communication import RecvIntOp, RecvFloatOp
from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.operations.order import (
    EqualsOp,
    LessThanOp,
    GreaterThanOp,
    LessThanOrEqualsOp,
    GreaterThanOrEqualsOp,
    NotEqualsOp,
)
from qoala.ast.value import QoalaInteger, QoalaFloat, Signedness
from qoala.errors import (
    InvalidArrayArgumentError,
    NotUnsignedIntegerArgumentError,
    NotIntegerArgumentError,
)
from qoala.operations import Remote
from qoala.operations.branching import if_cond
from qoala.operations.communication import recv_int, recv_float
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int32, UInt32, Int
from qoala.types.quantum import Entangle, LocalQubit
from tests.helpers_tests import DummyQoalaProgram


class TestNumbersSemantics:
    numeric_test_data = [(10, 20, Int32, QoalaInteger), (11.1, 22.2, Float, QoalaFloat)]

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

    @pytest.mark.parametrize(
        "val_a, val_b, numeric_type, internal_type", numeric_test_data
    )
    def test_basic_numeric_semantics(
        self,
        val_a: int | float,
        val_b: int | float,
        numeric_type: Int32 | Float,
        internal_type: QoalaInteger | QoalaFloat,
    ):
        int_a = numeric_type(val_a)
        int_b = numeric_type(val_b)
        int_c = int_a + int_b
        int_d = int_a - int_b
        int_e = int_a * int_b
        int_f = int_a / int_b

        # From the syntax tests, we know that all the statements above
        # return a QoalaExpression. We now want to test for the specific
        # type and the content within it
        assert isinstance(int_a, internal_type)
        assert isinstance(int_b, internal_type)
        assert isinstance(int_c, Add)
        assert isinstance(int_d, Subtract)
        assert isinstance(int_e, Multiply)
        assert isinstance(int_f, Divide)

        assert int_a.width == 32
        if numeric_type == Int32:
            assert int_a.signedness == Signedness.SIGNED
        elif numeric_type == Float:
            assert int_a.signedness == Signedness.UNKNOWN
        else:
            pytest.fail("Unknown numeric type")
        assert int_a.value == val_a

        assert int_b.width == 32
        if numeric_type == Int32:
            assert int_a.signedness == Signedness.SIGNED
        elif numeric_type == Float:
            assert int_a.signedness == Signedness.UNKNOWN
        else:
            pytest.fail("Unknown numeric base type")
        assert int_b.value == val_b

        assert int_c.operand_a is int_a
        assert int_c.operand_b is int_b

        assert int_d.operand_a is int_a
        assert int_d.operand_b is int_b

        assert int_e.operand_a is int_a
        assert int_e.operand_b is int_b

        assert int_f.operand_a is int_a
        assert int_f.operand_b is int_b

    def test_wrong_numeric_initialization(self):
        with pytest.raises(NotUnsignedIntegerArgumentError) as ex:
            _ = UInt32(-10)
        assert str(ex.value) == "'UInt32' type only supports positive integer values"

        with pytest.raises(NotIntegerArgumentError) as ex:
            _ = Int32(10.2)
        assert str(ex.value) == "'Int32' type only supports integer values"

        with pytest.raises(NotIntegerArgumentError) as ex:
            _ = UInt32(0.25)
        assert str(ex.value) == "'UInt32' type only supports integer values"

        with pytest.raises(NotIntegerArgumentError) as ex:
            _ = UInt32(-3.25)
        assert str(ex.value) == "'UInt32' type only supports integer values"

    def test_wrong_array_initialization(self):
        with pytest.raises(InvalidArrayArgumentError) as ex:
            _ = IntArray(10.2)
        assert (
            str(ex.value)
            == "Array of type 'IntArray' can only hold values of type 'int'"
        )
        with pytest.raises(InvalidArrayArgumentError) as ex:
            _ = FloatArray(10)
        assert (
            str(ex.value)
            == "Array of type 'FloatArray' can only hold values of type 'float'"
        )

    def test_order_operations_no_immediate(self):
        result_a = Int(10) < Int(20)
        result_b = Int(10) <= Int(20)
        result_c = Int(10) > Int(20)
        result_d = Int(10) >= Int(20)
        result_e = Int(10) == Int(20)

        assert isinstance(result_a, LessThanOp)
        assert isinstance(result_a.operand_a, QoalaInteger)
        assert result_a.operand_a.value == 10
        assert isinstance(result_a.operand_b, QoalaInteger)
        assert result_a.operand_b.value == 20

        assert isinstance(result_b, LessThanOrEqualsOp)
        assert isinstance(result_b.operand_a, QoalaInteger)
        assert result_b.operand_a.value == 10
        assert isinstance(result_b.operand_b, QoalaInteger)
        assert result_b.operand_b.value == 20

        assert isinstance(result_c, GreaterThanOp)
        assert isinstance(result_c.operand_a, QoalaInteger)
        assert result_c.operand_a.value == 10
        assert isinstance(result_c.operand_b, QoalaInteger)
        assert result_c.operand_b.value == 20

        assert isinstance(result_d, GreaterThanOrEqualsOp)
        assert isinstance(result_d.operand_a, QoalaInteger)
        assert result_d.operand_a.value == 10
        assert isinstance(result_d.operand_b, QoalaInteger)
        assert result_d.operand_b.value == 20

        assert isinstance(result_e, EqualsOp)
        assert isinstance(result_e.operand_a, QoalaInteger)
        assert result_e.operand_a.value == 10
        assert isinstance(result_e.operand_b, QoalaInteger)
        assert result_e.operand_b.value == 20

    def test_order_operations_immediate_right(self):
        result_a = Int(10) < 20
        result_b = Int(10) <= 20
        result_c = Int(10) > 20
        result_d = Int(10) >= 20
        result_e = Int(10) == 20

        assert isinstance(result_a, LessThanOp)
        assert isinstance(result_a.operand_a, QoalaInteger)
        assert result_a.operand_a.value == 10
        assert isinstance(result_a.operand_b, QoalaInteger)
        assert result_a.operand_b.value == 20

        assert isinstance(result_b, LessThanOrEqualsOp)
        assert isinstance(result_b.operand_a, QoalaInteger)
        assert result_b.operand_a.value == 10
        assert isinstance(result_b.operand_b, QoalaInteger)
        assert result_b.operand_b.value == 20

        assert isinstance(result_c, GreaterThanOp)
        assert isinstance(result_c.operand_a, QoalaInteger)
        assert result_c.operand_a.value == 10
        assert isinstance(result_c.operand_b, QoalaInteger)
        assert result_c.operand_b.value == 20

        assert isinstance(result_d, GreaterThanOrEqualsOp)
        assert isinstance(result_d.operand_a, QoalaInteger)
        assert result_d.operand_a.value == 10
        assert isinstance(result_d.operand_b, QoalaInteger)
        assert result_d.operand_b.value == 20

        assert isinstance(result_e, EqualsOp)
        assert isinstance(result_e.operand_a, QoalaInteger)
        assert result_e.operand_a.value == 10
        assert isinstance(result_e.operand_b, QoalaInteger)
        assert result_e.operand_b.value == 20

    def test_order_operations_immediate_left(self):
        result_a = 10 < Int(20)
        result_b = 10 <= Int(20)
        result_c = 10 > Int(20)
        result_d = 10 >= Int(20)
        result_e = 10 == Int(20)

        # Since there is no (for example) "__rge__" dunder method, python
        # will *invert* the inequality to apply the "__ge__" method, which
        # receives the QoalaInteger type on the left:
        # 10 < Int(20) -> Int(20) > 10 -> can apply QoalaInteger.__ge__
        assert isinstance(result_a, GreaterThanOp)
        assert isinstance(result_b, GreaterThanOrEqualsOp)
        assert isinstance(result_c, LessThanOp)
        assert isinstance(result_d, LessThanOrEqualsOp)
        assert isinstance(result_e, EqualsOp)

    def test_order_operations_mixed_types(self):
        result_a = Float(10) < Int(20)
        result_b = Float(10) <= Int(20)
        result_c = Float(10) > Int(20)
        result_d = Float(10) >= Int(20)
        result_e = Float(10) == Int(20)

        assert isinstance(result_a, LessThanOp)
        assert isinstance(result_a.operand_a, QoalaFloat)
        assert result_a.operand_a.value == 10
        assert isinstance(result_a.operand_b, IntToFloat)
        assert isinstance(result_a.operand_b.operand, QoalaInteger)
        assert result_a.operand_b.operand.value == 20

        assert isinstance(result_b, LessThanOrEqualsOp)
        assert isinstance(result_b.operand_a, QoalaFloat)
        assert result_b.operand_a.value == 10
        assert isinstance(result_b.operand_b, IntToFloat)
        assert isinstance(result_b.operand_b.operand, QoalaInteger)
        assert result_b.operand_b.operand.value == 20

        assert isinstance(result_c, GreaterThanOp)
        assert isinstance(result_c.operand_a, QoalaFloat)
        assert result_c.operand_a.value == 10
        assert isinstance(result_c.operand_b, IntToFloat)
        assert isinstance(result_c.operand_b.operand, QoalaInteger)
        assert result_c.operand_b.operand.value == 20

        assert isinstance(result_d, GreaterThanOrEqualsOp)
        assert isinstance(result_d.operand_a, QoalaFloat)
        assert result_d.operand_a.value == 10
        assert isinstance(result_d.operand_b, IntToFloat)
        assert isinstance(result_d.operand_b.operand, QoalaInteger)
        assert result_d.operand_b.operand.value == 20

        assert isinstance(result_e, EqualsOp)
        assert isinstance(result_e.operand_a, QoalaFloat)
        assert result_e.operand_a.value == 10
        assert isinstance(result_e.operand_b, IntToFloat)
        assert isinstance(result_e.operand_b.operand, QoalaInteger)
        assert result_e.operand_b.operand.value == 20

    def test_singular_recv_int_value_comparison(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        Remote("Alice")
        qubit = Entangle("Alice")
        local_qubit = LocalQubit()
        x = recv_int("Alice")

        with if_cond(x == 0) as (branch_true, branch_false):
            with branch_true:
                qubit.X()
            with branch_false:
                local_qubit.Z()

        main_block = QoalaProgram._instance.current_function()._main_block

        assert len(main_block.operations) == 6
        # In this example, we only assert that the value returned by recv_int can be
        # compared as any other integer.
        assert isinstance(main_block.operations[2], RecvIntOp)
        assert isinstance(main_block.operations[4], EqualsOp)
        assert (
            main_block.operations[4].operand_a is main_block.operations[2]
            or main_block.operations[4].operand_b is main_block.operations[2]
        )
        assert isinstance(main_block.operations[5], ConditionalBranching)

        del QoalaProgram._declared_remotes
        del QoalaProgram._compilation_context

    def test_singular_recv_float_value_comparison(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        Remote("Alice")
        qubit = Entangle("Alice")
        local_qubit = LocalQubit()
        x = recv_float("Alice")

        with if_cond(x == 0.0) as (branch_true, branch_false):
            with branch_true:
                qubit.X()
            with branch_false:
                local_qubit.Z()

        main_block = QoalaProgram._instance.current_function()._main_block

        assert len(main_block.operations) == 6
        # In this example, we only assert that the value returned by recv_int can be
        # compared as any other integer.
        assert isinstance(main_block.operations[2], RecvFloatOp)
        assert isinstance(main_block.operations[4], EqualsOp)
        assert (
            main_block.operations[4].operand_a is main_block.operations[2]
            or main_block.operations[4].operand_b is main_block.operations[2]
        )
        assert isinstance(main_block.operations[5], ConditionalBranching)

        del QoalaProgram._declared_remotes
        del QoalaProgram._compilation_context

    def test_compare_qubit_measurement_comparison(self):
        # We also manually set the internal structures for registering remotes and compilation options
        QoalaProgram._declared_remotes = {}
        compilation_context = CompilationContext()
        compilation_context.options.use_singular_classical_comm_ops = True
        QoalaProgram._compilation_context = compilation_context

        remote = Remote("Bob")
        q1 = LocalQubit()
        # This operation yields a Bit
        int_m = q1.measure()
        int_c = recv_int(remote)

        # We compare a measure (integer of width 1) with a recv_int (integer of width 32)
        # In this case we need to upcast the bit to an integer
        cmp = int_m != int_c

        main_block = QoalaProgram._instance.current_function()._main_block

        # Here we expect 5 operations:
        # qubit, measure, recv_int, cast(bit to int), NotEquals
        assert len(main_block.operations) == 5
        # In this example, we only assert that the value returned by recv_int can be
        # compared as any other integer.

        assert isinstance(main_block.operations[2], RecvIntOp)
        assert isinstance(main_block.operations[3], BitToInt)
        assert isinstance(main_block.operations[4], NotEqualsOp)
        assert (
            main_block.operations[4].operand_a is main_block.operations[3]
            or main_block.operations[4].operand_b is main_block.operations[3]
        )

        del QoalaProgram._declared_remotes
        del QoalaProgram._compilation_context
