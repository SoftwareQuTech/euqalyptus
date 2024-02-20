from qoala import QoalaProgram
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
    inc_e = int_b * int_a
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

    def test_program_using_args(self):
        program_with_arg.compile(1, 2.5)

        assert len(program_with_arg._body) == 2

    def test_program_with_array(self):
        program_with_array_access.compile()

        assert len(program_with_array_access._body) == 4

    def test_program_with_array_mutation(self):
        program_with_array_mutation.compile()

        assert len(program_with_array_mutation._body) == 6

