from qoala import QoalaProgram
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
