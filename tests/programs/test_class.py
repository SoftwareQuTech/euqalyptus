from typing import List, Any

from qoala import QoalaProgramBase
from qoala.ast.operations.arrays import GetItem, SetItem
from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaArray
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int


class EmptyProgram(QoalaProgramBase):
    def main(self, args: List[Any]) -> int:
        pass


class ArithmeticProgram(QoalaProgramBase):
    def main(self):
        int_a = Int(10)
        int_b = Int(20)

        int_c = int_a + int_b
        inc_d = int_b - int_a
        inc_e = int_a * int_a
        inc_f = int_b / int_a


class ProgramWithArg(QoalaProgramBase):
    def main(self, val_a: int, val_b: float):
        int_a = Int(val_a)
        int_b = Float(val_b)


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


# @pytest.mark.skip(reason="Qoala programs declaration using class inheritance is not implemented yet")
class TestQoalaClass:
    def test_mt_program(self):
        empty_program = EmptyProgram()
        empty_program.compile(list())

        assert len(empty_program._body) == 0

    def test_basic_arith_program(self):
        arithmetic_program = ArithmeticProgram()
        arithmetic_program.compile()

        assert len(arithmetic_program._body) == 6
        assert isinstance(arithmetic_program._body[0], QoalaInteger)
        assert isinstance(arithmetic_program._body[1], QoalaInteger)
        assert isinstance(arithmetic_program._body[2], Add)
        assert arithmetic_program._body[2].operand_a is arithmetic_program._body[0]
        assert arithmetic_program._body[2].operand_b is arithmetic_program._body[1]
        assert isinstance(arithmetic_program._body[3], Subtract)
        assert arithmetic_program._body[3].operand_a is arithmetic_program._body[1]
        assert arithmetic_program._body[3].operand_b is arithmetic_program._body[0]
        assert isinstance(arithmetic_program._body[4], Multiply)
        assert arithmetic_program._body[4].operand_a is arithmetic_program._body[0]
        assert arithmetic_program._body[4].operand_b is arithmetic_program._body[0]
        assert isinstance(arithmetic_program._body[5], Divide)
        assert arithmetic_program._body[5].operand_a is arithmetic_program._body[1]
        assert arithmetic_program._body[5].operand_b is arithmetic_program._body[0]

    def test_program_using_args(self):
        program_with_arg = ProgramWithArg()
        program_with_arg.compile(1, 2.5)

        assert len(program_with_arg._body) == 2
        assert isinstance(program_with_arg._body[0], QoalaInteger)
        assert isinstance(program_with_arg._body[1], QoalaFloat)

    def test_program_with_array_access(self):
        program_with_array_access = ProgramWithArrayAccess()
        program_with_array_access.compile()

        assert len(program_with_array_access._body) == 5
        assert isinstance(program_with_array_access._body[0], QoalaInteger)
        assert isinstance(program_with_array_access._body[1], QoalaInteger)
        assert isinstance(program_with_array_access._body[2], QoalaArray)
        assert program_with_array_access._body[2].base_type == int
        assert program_with_array_access._body[2].base_size == 32
        assert program_with_array_access._body[2].length == 2
        assert isinstance(program_with_array_access._body[2].members[0], QoalaInteger)
        assert isinstance(program_with_array_access._body[2].members[1], QoalaInteger)
        assert isinstance(program_with_array_access._body[3], QoalaInteger)
        assert isinstance(program_with_array_access._body[4], GetItem)
        assert program_with_array_access._body[4].base_array is program_with_array_access._body[2]
        assert program_with_array_access._body[4].index is program_with_array_access._body[3]

    def test_program_with_array_mutation(self):
        program_with_array_mutation = ProgramWithArrayMutation()
        program_with_array_mutation.compile()

        assert len(program_with_array_mutation._body) == 6
        assert isinstance(program_with_array_mutation._body[0], QoalaArray)
        assert program_with_array_mutation._body[0].base_type == float
        assert program_with_array_mutation._body[0].base_size == 32
        assert program_with_array_mutation._body[0].length == 0
        assert isinstance(program_with_array_mutation._body[1], QoalaArray)
        assert program_with_array_mutation._body[1].base_type == int
        assert program_with_array_mutation._body[1].base_size == 32
        assert program_with_array_mutation._body[1].length == 0
        assert isinstance(program_with_array_mutation._body[2], QoalaFloat)
        assert isinstance(program_with_array_mutation._body[3], SetItem)
        assert program_with_array_mutation._body[3].base_array is program_with_array_mutation._body[0]
        assert program_with_array_mutation._body[3].index is program_with_array_mutation._body[2]
        assert isinstance(program_with_array_mutation._body[4], QoalaInteger)
        assert isinstance(program_with_array_mutation._body[5], SetItem)
        assert program_with_array_mutation._body[5].base_array is program_with_array_mutation._body[1]
        assert program_with_array_mutation._body[5].index is program_with_array_mutation._body[4]
