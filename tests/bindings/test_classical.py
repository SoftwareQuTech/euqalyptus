import pytest

from qoala import QoalaProgram, QoalaModule, NotYetCompiledError
from qoala.types.classical.floats import Float
from qoala.types.classical.integer import Int
from qoala.types.classical.arrays import IntArray, FloatArray


@QoalaProgram
def empty_program():
    pass


@QoalaProgram
def simple_arith_program():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b
    int_d = int_a - int_b
    int_e = int_a * int_b
    int_f = int_a / int_b

    float_a = Float(10.0)
    float_b = Float(20.0)

    float_c = float_a + float_b
    float_d = float_a - float_b
    float_e = float_a * float_b
    float_f = float_a / float_b


@QoalaProgram
def simple_arith_program_composed():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b

    float_a = Float(10.0)
    float_b = Float(20.0)

    float_c = float_a - float_b

    int_A = Int(20)
    int_B = Int(5)
    # int_c uses an integer, but also a "composed" expression (addition)
    # which can evaluate to an integer
    int_d = int_A * int_c
    int_e = int_d / int_B

    float_A = Float(20.0)
    float_B = Float(4.0)
    # float_c uses a float, but also a "composed" expression (sustraction)
    # which can evaluate to an integer
    float_d = float_c * float_A
    float_e = float_d / float_B


@QoalaProgram
def simple_arith_program_immediates():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b

    float_a = Float(10.0)
    float_b = Float(20.0)

    float_c = float_a - float_b

    # int_d uses an "immediate", declared as a qoala type
    int_d = Int(5) * int_c
    # int_e uses an immediate declared as a python integer
    # this test automatic casting from python types to qoala types
    int_e = int_d / 5

    # float_d uses an "immediate", declared as a qoala type
    float_d = float_c * Float(20.0)
    # float_e uses an immediate declared as a python float
    # this test automatic casting from python types to qoala types
    float_e = float_d / 4.0


@QoalaProgram
def arrays_program():
    int_array = IntArray(Int(10), 20)
    float_array = FloatArray(Float(5.5), 1.4)

    int_res = int_array[1]
    float_red = float_array[Int(1)]

    # int_array.store(30)
    # float_array.store(Float(3.14))


class TestQoalaHIRPythonBindingsClassical:
    def test_empty_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = empty_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = empty_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  func.func @empty_program() {
    return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_simple_arith_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  func.func @simple_arith_program() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %0 = arith.addi %c10_i32, %c20_i32 : i32
    %1 = arith.subi %c10_i32, %c20_i32 : i32
    %2 = arith.muli %c10_i32, %c20_i32 : i32
    %3 = arith.divui %c10_i32, %c20_i32 : i32
    %cst = arith.constant 1.000000e+01 : f32
    %cst_0 = arith.constant 2.000000e+01 : f32
    %4 = arith.addf %cst, %cst_0 : f32
    %5 = arith.subf %cst, %cst_0 : f32
    %6 = arith.mulf %cst, %cst_0 : f32
    %7 = arith.divf %cst, %cst_0 : f32
    return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_composed_arith_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program_composed.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program_composed.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  func.func @simple_arith_program_composed() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %0 = arith.addi %c10_i32, %c20_i32 : i32
    %cst = arith.constant 1.000000e+01 : f32
    %cst_0 = arith.constant 2.000000e+01 : f32
    %1 = arith.subf %cst, %cst_0 : f32
    %c20_i32_1 = arith.constant 20 : i32
    %c5_i32 = arith.constant 5 : i32
    %2 = arith.muli %c20_i32_1, %0 : i32
    %3 = arith.divui %2, %c5_i32 : i32
    %cst_2 = arith.constant 2.000000e+01 : f32
    %cst_3 = arith.constant 4.000000e+00 : f32
    %4 = arith.mulf %1, %cst_2 : f32
    %5 = arith.divf %4, %cst_3 : f32
    return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_arith_program_with_immediates_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program_immediates.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program_immediates.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  func.func @simple_arith_program_immediates() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %0 = arith.addi %c10_i32, %c20_i32 : i32
    %cst = arith.constant 1.000000e+01 : f32
    %cst_0 = arith.constant 2.000000e+01 : f32
    %1 = arith.subf %cst, %cst_0 : f32
    %c5_i32 = arith.constant 5 : i32
    %2 = arith.muli %c5_i32, %0 : i32
    %c5_i32_1 = arith.constant 5 : i32
    %3 = arith.divui %2, %c5_i32_1 : i32
    %cst_2 = arith.constant 2.000000e+01 : f32
    %4 = arith.mulf %1, %cst_2 : f32
    %cst_3 = arith.constant 4.000000e+00 : f32
    %5 = arith.divf %4, %cst_3 : f32
    return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_arrays_program_to_qoala_hir(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = arrays_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = arrays_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  func.func @arrays_program() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %from_elements = tensor.from_elements %c10_i32, %c20_i32 : tensor<2x1xi32>
    %cst = arith.constant 5.500000e+00 : f32
    %cst_0 = arith.constant 1.400000e+00 : f32
    %from_elements_1 = tensor.from_elements %cst, %cst_0 : tensor<2x1xf32>
    %c1 = arith.constant 1 : index
    %1 = tensor.extract %from_elements[%c1] : i32
    %c1_i32_0 = arith.constant 1 : i32
    %2 = arith.index_cast %c1_i32_0 : index
    %3 = tensor.extract %from_elements_1[%2] : f32
    return
  }
}
"""
        assert str(module.asm) == expected_asm
