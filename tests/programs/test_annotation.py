from qoala import QoalaProgram
from qoala.ast.operations.arrays import GetItem, SetItem
from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.operations.quantum import (
    XGate,
    YGate,
    ZGate,
    TGate,
    HGate,
    SGate,
    QubitMeasure,
    RotateX,
    RotateY,
    RotateZ,
    CNotGate,
)
from qoala.ast.qubit import QoalaLocalQubit
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaArray
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.quantum.qubit import LocalQubit


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


@QoalaProgram
def program_local_qubit_with_simple_gates():
    qubit = LocalQubit()

    qubit.X()
    qubit.Y()
    qubit.Z()
    qubit.T()
    qubit.H()
    qubit.S()

    measurement = qubit.measure()


@QoalaProgram
def program_local_qubit_with_complex_gates():
    n_val = Int(20)
    d_val = Int(30)
    angle_val = Float(21.2)

    qubit = LocalQubit()
    qubit_b = LocalQubit()

    qubit.rot_X(n=10, d=30)
    qubit.rot_Y(n=10, d=d_val, angle=10.5)
    qubit.rot_Z(n=n_val, d=d_val, angle=angle_val)

    qubit.cnot(qubit_b)
    # CPhase gates cannot be compiled yet
    # qubit.cphase(qubit_b)

    measurement_a = qubit.measure()
    measurement_b = qubit_b.measure()


# Across all the tests of this file, we only make assertions on the AST, so we compile "lazily"
# (do not transform the AST into Qoala HIR
class TestQoalaDecorator:

    def test_decorator_on_mt_program(self):
        empty_program.compile(compile_lazy=True)
        # The second invocation to "compile" should not do anything, since the program
        # was already compiled
        empty_program.compile(compile_lazy=True)

        # Basic check
        assert len(empty_program.module.functions) == 1
        assert len(empty_program.module.functions[0].blocks) == 1
        assert len(empty_program.module.functions[0].blocks[0].operations) == 0

    def test_basic_arith_program(self):
        arithmetic_program.compile(compile_lazy=True)

        # Basic check
        assert len(arithmetic_program.module.functions) == 1
        assert len(arithmetic_program.module.functions[0].blocks) == 1
        assert len(arithmetic_program.module.functions[0].blocks[0].operations) == 6
        program_body = arithmetic_program.module.functions[0].blocks[0].operations

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

    def test_program_using_args(self):
        program_with_arg.compile(1, 2.5, compile_lazy=True)

        # Basic check
        assert len(program_with_arg.module.functions) == 1
        assert len(program_with_arg.module.functions[0].blocks) == 1
        assert len(program_with_arg.module.functions[0].blocks[0].operations) == 2
        program_body = program_with_arg.module.functions[0].blocks[0].operations

        assert isinstance(program_body[0], QoalaInteger)
        assert isinstance(program_body[1], QoalaFloat)

    def test_program_with_array_access(self):
        program_with_array_access.compile(compile_lazy=True)

        # Basic check
        assert len(program_with_array_access.module.functions) == 1
        assert len(program_with_array_access.module.functions[0].blocks) == 1
        assert (
            len(program_with_array_access.module.functions[0].blocks[0].operations) == 5
        )
        program_body = (
            program_with_array_access.module.functions[0].blocks[0].operations
        )

        assert isinstance(program_body[0], QoalaInteger)
        assert isinstance(program_body[1], QoalaInteger)
        assert isinstance(program_body[2], QoalaArray)
        assert program_body[2].base_type is int
        assert program_body[2].base_size is 32
        assert program_body[2].length is 2
        assert isinstance(program_body[2].members[0], QoalaInteger)
        assert isinstance(program_body[2].members[1], QoalaInteger)
        assert isinstance(program_body[3], QoalaInteger)
        assert isinstance(program_body[4], GetItem)
        assert program_body[4].base_array is program_body[2]
        assert program_body[4].index is program_body[3]

    def test_program_with_array_mutation(self):
        program_with_array_mutation.compile(compile_lazy=True)

        # Basic check
        assert len(program_with_array_mutation.module.functions) == 1
        assert len(program_with_array_mutation.module.functions[0].blocks) == 1
        assert (
            len(program_with_array_mutation.module.functions[0].blocks[0].operations)
            == 6
        )
        program_body = (
            program_with_array_mutation.module.functions[0].blocks[0].operations
        )

        assert isinstance(program_body[0], QoalaArray)
        assert program_body[0].base_type is float
        assert program_body[0].base_size == 32
        assert program_body[0].length == 0
        assert isinstance(program_body[1], QoalaArray)
        assert program_body[1].base_type is int
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

    def test_quantum_program_with_simple_gates(self):
        program_local_qubit_with_simple_gates.compile(compile_lazy=True)

        # Basic check
        assert len(program_local_qubit_with_simple_gates.module.functions) == 1
        assert (
            len(program_local_qubit_with_simple_gates.module.functions[0].blocks) == 1
        )
        assert (
            len(
                program_local_qubit_with_simple_gates.module.functions[0]
                .blocks[0]
                .operations
            )
            == 10
        )
        program_body = (
            program_local_qubit_with_simple_gates.module.functions[0]
            .blocks[0]
            .operations
        )

        assert isinstance(program_body[0], QoalaLocalQubit)
        assert isinstance(program_body[1], XGate)
        assert program_body[1].qubit is program_body[0]
        assert isinstance(program_body[2], YGate)
        assert program_body[2].qubit is program_body[0]
        assert isinstance(program_body[3], ZGate)
        assert program_body[3].qubit is program_body[0]
        assert isinstance(program_body[4], QoalaFloat)
        assert program_body[4].value == 0.7853981633974483
        assert isinstance(program_body[5], TGate)
        assert isinstance(program_body[5], RotateZ)
        assert program_body[5].qubit is program_body[0]
        assert program_body[5].angle is program_body[4]
        assert isinstance(program_body[6], HGate)
        assert program_body[6].qubit is program_body[0]
        assert isinstance(program_body[7], QoalaFloat)
        assert program_body[7].value == 1.5707963267948966
        assert isinstance(program_body[8], SGate)
        assert isinstance(program_body[8], RotateZ)
        assert program_body[8].qubit is program_body[0]
        assert program_body[8].angle is program_body[7]
        assert isinstance(program_body[9], QubitMeasure)

    def test_quantum_program_with_complex_gates(self):
        program_local_qubit_with_complex_gates.compile(compile_lazy=True)

        # Basic check
        assert len(program_local_qubit_with_complex_gates.module.functions) == 1
        assert (
            len(program_local_qubit_with_complex_gates.module.functions[0].blocks) == 1
        )
        assert (
            len(
                program_local_qubit_with_complex_gates.module.functions[0]
                .blocks[0]
                .operations
            )
            == 13
        )
        program_body = (
            program_local_qubit_with_complex_gates.module.functions[0]
            .blocks[0]
            .operations
        )

        assert isinstance(program_body[0], QoalaInteger)
        assert isinstance(program_body[1], QoalaInteger)
        assert isinstance(program_body[2], QoalaFloat)
        assert isinstance(program_body[3], QoalaLocalQubit)
        assert isinstance(program_body[4], QoalaLocalQubit)
        # This is the angle value computed at compile time for n = 10 and d = 30, immediate
        # arguments of the rot_X operation
        assert isinstance(program_body[5], QoalaFloat)
        assert program_body[5].value == 2.9258361585343192e-08
        assert isinstance(program_body[6], RotateX)
        assert program_body[6].qubit is program_body[3]
        assert program_body[6].angle is program_body[5]
        # The next rotation will use the immediate value of the angle, ignoring the values of "n" and "d"
        # The given angle value:
        assert isinstance(program_body[7], QoalaFloat)
        assert program_body[7].value == 10.5
        # Rotate operation
        assert isinstance(program_body[8], RotateY)
        assert program_body[8].qubit is program_body[3]
        assert program_body[8].angle is program_body[7]
        # The "rot_Z" operation uses an angle value from a constant declared above
        # Rotation operation
        assert isinstance(program_body[9], RotateZ)
        assert program_body[9].qubit is program_body[3]
        assert program_body[9].angle is program_body[2]

        assert isinstance(program_body[10], CNotGate)
        assert program_body[10].qubit is program_body[3]
        assert program_body[10].target is program_body[4]
        assert isinstance(program_body[11], QubitMeasure)
        assert program_body[11].qubit is program_body[3]

        assert isinstance(program_body[12], QubitMeasure)
        assert program_body[12].qubit is program_body[4]
