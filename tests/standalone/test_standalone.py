from qoala import QoalaProgram
from qoala.ast.operations.arrays import GetItem, SetItem
from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaArray
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int


@QoalaProgram
def empty_program():
    pass


@QoalaProgram
def arithmetic_program():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b
    inc_d = int_b - int_a
    inc_e = int_a * int_a
    inc_f = int_b / int_a


@QoalaProgram
def program_with_arg(val_a: int, val_b: float):
    int_a = Int(val_a)
    int_b = Float(val_b)


@QoalaProgram
def program_with_array_access():
    int_a = Int(15)
    arr_a = IntArray(10, int_a)

    elem = arr_a[1]


@QoalaProgram
def program_with_array_mutation():
    arr = FloatArray()
    arr_b = IntArray()

    arr.store(10.2)
    arr_b.store(5)


class TestQoalaDecorator:
    def test_decorator_on_mt_program(self):
        empty_program.compile()

        assert len(empty_program._body) == 0

    def test_basic_arith_program(self):
        arithmetic_program.compile()

        assert len(arithmetic_program._body) == 6
        assert isinstance(arithmetic_program._body[0], QoalaInteger)
        assert isinstance(arithmetic_program._body[1], QoalaInteger)
        assert isinstance(arithmetic_program._body[2], Add)
        assert arithmetic_program._body[2].operand_a == arithmetic_program._body[0]
        assert arithmetic_program._body[2].operand_b == arithmetic_program._body[1]
        assert isinstance(arithmetic_program._body[3], Subtract)
        assert arithmetic_program._body[3].operand_a == arithmetic_program._body[1]
        assert arithmetic_program._body[3].operand_b == arithmetic_program._body[0]
        assert isinstance(arithmetic_program._body[4], Multiply)
        assert arithmetic_program._body[4].operand_a == arithmetic_program._body[0]
        assert arithmetic_program._body[4].operand_b == arithmetic_program._body[0]
        assert isinstance(arithmetic_program._body[5], Divide)
        assert arithmetic_program._body[5].operand_a == arithmetic_program._body[1]
        assert arithmetic_program._body[5].operand_b == arithmetic_program._body[0]

    def test_program_using_args(self):
        program_with_arg.compile(1, 2.5)

        assert len(program_with_arg._body) == 2
        assert isinstance(program_with_arg._body[0], QoalaInteger)
        assert isinstance(program_with_arg._body[1], QoalaFloat)

    def test_program_with_array_access(self):
        program_with_array_access.compile()

        assert len(program_with_array_access._body) == 5
        assert isinstance(program_with_array_access._body[0], QoalaInteger)
        assert isinstance(program_with_array_access._body[1], QoalaInteger)
        assert isinstance(program_with_array_access._body[2], QoalaArray)
        assert program_with_array_access._body[2].base_type == int
        assert program_with_array_access._body[2].base_size == 32
        assert program_with_array_access._body[2].length == 2
        assert isinstance(program_with_array_access._body[2].elements[0], QoalaInteger)
        assert isinstance(program_with_array_access._body[2].elements[1], QoalaInteger)
        assert isinstance(program_with_array_access._body[3], GetItem)
        assert isinstance(program_with_array_access._body[4], QoalaInteger)
        assert program_with_array_access._body[3].base_array == program_with_array_access._body[2]
        assert program_with_array_access._body[3].index == program_with_array_access._body[4]

    def test_program_with_array_mutation(self):
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
        assert program_with_array_mutation._body[3].base_array == program_with_array_mutation._body[0]
        assert program_with_array_mutation._body[3].index == program_with_array_mutation._body[2]
        assert isinstance(program_with_array_mutation._body[4], QoalaInteger)
        assert isinstance(program_with_array_mutation._body[5], SetItem)
        assert program_with_array_mutation._body[5].base_array == program_with_array_mutation._body[1]
        assert program_with_array_mutation._body[5].index == program_with_array_mutation._body[4]
