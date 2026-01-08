from typing import List, Any

from qoala import QoalaProgramBase
from qoala.ast.operations.arrays import GetItem, SetItem
from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.operations.control_flow import ReturnResultsOp
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaArray
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.operations.control_flow import return_results


class EmptyProgram(QoalaProgramBase):

    def main(self, args: List[Any]) -> int:
        pass


class ArithmeticProgram(QoalaProgramBase):

    def main(self):
        int_a = Int(10)
        int_b = Int(20)

        int_c = int_a + int_b
        int_d = int_b - int_a
        int_e = int_a * int_a
        int_f = int_b / int_a

        return_results(int_c, int_d, int_e, int_f)


class ProgramWithArg(QoalaProgramBase):

    def main(self, val_a: int, val_b: float):
        int_a = Int(val_a)
        int_b = Float(val_b)

        return_results(int_a, int_b)


class ProgramWithArrayAccess(QoalaProgramBase):

    def main(self):
        int_a = Int(15)
        arr_a = IntArray(10, int_a)

        elem = arr_a[1]


class ProgramWithArrayMutation(QoalaProgramBase):

    def main(self):
        arr = FloatArray()
        arr_b = IntArray()

        arr.store(10.2)
        arr_b.store(5)


# Across all the tests of this file, we only make assertions on the AST, so we compile "lazily"
# (do not transform the AST into Qoala HIR
class TestQoalaClass:
    def test_mt_program(self):
        empty_program = EmptyProgram()
        empty_program.compile(list(), compile_lazy=True)
        # The second invocation to "compile" should not do anything, since the program
        # was already compiled
        empty_program.compile(list(), compile_lazy=True)

        # We *expect* 1 function, with 1 block, which is empty
        assert len(empty_program.module.functions) == 1
        assert len(empty_program.module.functions[0]._main_block.operations) == 0

    def test_basic_arith_program(self):
        arithmetic_program = ArithmeticProgram()
        arithmetic_program.compile(compile_lazy=True)

        # Basic check
        assert len(arithmetic_program.module.functions) == 1
        assert len(arithmetic_program.module.functions[0]._main_block.operations) == 7
        program_body = arithmetic_program.module.functions[0]._main_block.operations

        assert isinstance(program_body[0], QoalaInteger)
        assert isinstance(program_body[1], QoalaInteger)
        assert isinstance(program_body[2], Add)
        assert program_body[2].operand_a is program_body[0]
        assert program_body[2].operand_b is program_body[1]
        assert isinstance(program_body[3], Subtract)
        assert program_body[3].operand_a is program_body[1]
        assert program_body[3].operand_b is program_body[0]
        assert isinstance(program_body[4], Multiply)
        assert program_body[4].operand_a is program_body[0]
        assert program_body[4].operand_b is program_body[0]
        assert isinstance(program_body[5], Divide)
        assert program_body[5].operand_a is program_body[1]
        assert program_body[5].operand_b is program_body[0]
        assert isinstance(program_body[6], ReturnResultsOp)
        assert program_body[6].values == [
            program_body[2],
            program_body[3],
            program_body[4],
            program_body[5],
        ]

    def test_program_using_args(self):
        program_with_arg = ProgramWithArg()
        program_with_arg.compile(1, 2.5, compile_lazy=True)

        # Basic check
        assert len(program_with_arg.module.functions) == 1
        assert len(program_with_arg.module.functions[0]._main_block.operations) == 3
        program_body = program_with_arg.module.functions[0]._main_block.operations

        assert isinstance(program_body[0], QoalaInteger)
        assert isinstance(program_body[1], QoalaFloat)
        assert isinstance(program_body[2], ReturnResultsOp)
        assert program_body[2].values == [program_body[0], program_body[1]]

    def test_program_with_array_access(self):
        program_with_array_access = ProgramWithArrayAccess()
        program_with_array_access.compile(compile_lazy=True)

        # Basic check
        assert len(program_with_array_access.module.functions) == 1
        assert (
            len(program_with_array_access.module.functions[0]._main_block.operations) == 5
        )
        program_body = (
            program_with_array_access.module.functions[0]._main_block.operations
        )

        assert isinstance(program_body[0], QoalaInteger)
        assert isinstance(program_body[1], QoalaInteger)
        assert isinstance(program_body[2], QoalaArray)
        assert program_body[2].base_type == int
        assert program_body[2].base_size == 32
        assert program_body[2].length == 2
        assert isinstance(program_body[2].members[0], QoalaInteger)
        assert isinstance(program_body[2].members[1], QoalaInteger)
        assert isinstance(program_body[3], QoalaInteger)
        assert isinstance(program_body[4], GetItem)
        assert program_body[4].base_array is program_body[2]
        assert program_body[4].index is program_body[3]

    def test_program_with_array_mutation(self):
        program_with_array_mutation = ProgramWithArrayMutation()
        program_with_array_mutation.compile(compile_lazy=True)

        # Basic check
        assert len(program_with_array_mutation.module.functions) == 1
        assert (
            len(program_with_array_mutation.module.functions[0]._main_block.operations)
            == 6
        )
        program_body = (
            program_with_array_mutation.module.functions[0]._main_block.operations
        )

        assert len(program_body) == 6
        assert isinstance(program_body[0], QoalaArray)
        assert program_body[0].base_type == float
        assert program_body[0].base_size == 32
        assert program_body[0].length == 0
        assert isinstance(program_body[1], QoalaArray)
        assert program_body[1].base_type == int
        assert program_body[1].base_size == 32
        assert program_body[1].length == 0
        assert isinstance(program_body[2], QoalaFloat)
        assert isinstance(program_body[3], SetItem)
        assert program_body[3].base_array is program_body[0]
        assert program_body[3].index is program_body[2]
        assert isinstance(program_body[4], QoalaInteger)
        assert isinstance(program_body[5], SetItem)
        assert program_body[5].base_array is program_body[1]
        assert program_body[5].index is program_body[4]
