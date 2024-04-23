import pytest

from qoala import QoalaProgram, QoalaModule
from qoala.errors import NotYetCompiledError
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
    # float_c uses a float, but also a "composed" expression (subtraction)
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
def basic_arrays_program():
    int_array = IntArray(Int(10), 20)
    float_array = FloatArray(Float(5.5), 1.4)

    int_res = int_array[1]
    float_red = float_array[Int(1)]


@QoalaProgram
def array_with_mutation_program():
    int_array = IntArray(Int(10), 20)
    float_array = FloatArray(Float(5.5), 1.4)
    # This is an interesting case, since it does not mutate the values of the
    # involved aray (i.e. "no int_array[0] = 30", to override the "10"),
    # but rather expands the array to store one more value (redimension and store)
    int_array.store(30)
    float_array.store(Float(3.14))


class TestQoalaQnetPythonBindingsClassical:
    def test_empty_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = empty_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = empty_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @empty_program() {
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_simple_arith_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  qnet.func @simple_arith_program() {
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
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_composed_arith_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program_composed.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program_composed.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  qnet.func @simple_arith_program_composed() {
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
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_arith_program_with_immediates_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = simple_arith_program_immediates.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = simple_arith_program_immediates.compile()
        assert isinstance(module, QoalaModule)
        # Note 1 - The qoala type "Int", creates a _signed_ integer of 32 bits width. We use this information
        #          (the signedness) to create the MLIR arith builtin type using IntegerType.get_(un)signed(width).
        expected_asm = """module {
  qnet.func @simple_arith_program_immediates() {
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
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

    def test_arrays_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = basic_arrays_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = basic_arrays_program.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - According to the documentation "`tensor.extract` op reads a ranked tensor and returns one
        #        element as specified by the given indices. The result of the op is a value with the same
        #        type as the elements of the tensor."
        #        Despite that it says that the result type if of the type of the elements, the **pretty-printed**
        #        return type _is the type of the tensor of the tensor used to access_. This can be seen in the
        #        "assemblyFormat" property of the Tensor_ExtractOp class in the tensor dialect declaration,
        #        located in the file /mlir/installation/folder/mlir/Dialect/Tensor/IR/TensorOps.td
        #        If we request the "generic" version of the MLIR, we can notice the "real" return type of the extract
        #        (see below). Maybe this limitation is due to the fact that from the "extract" operation asmFormat
        #        property you cannot access the "$elementType" attribute of the tensor uses as an operand
        expected_asm = """module {
  qnet.func @basic_arrays_program() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %from_elements = tensor.from_elements %c10_i32, %c20_i32 : tensor<2xi32>
    %cst = arith.constant 5.500000e+00 : f32
    %cst_0 = arith.constant 1.400000e+00 : f32
    %from_elements_1 = tensor.from_elements %cst, %cst_0 : tensor<2xf32>
    %c1 = arith.constant 1 : index
    %extracted = tensor.extract %from_elements[%c1] : tensor<2xi32>
    %c1_i32 = arith.constant 1 : i32
    %0 = arith.index_cast %c1_i32 : i32 to index
    %extracted_2 = tensor.extract %from_elements_1[%0] : tensor<2xf32>
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm

        # See the returned valued of the operations on registers %7 and %10
        expected_generic_asm = """"builtin.module"() ({
  "qnet.func"() <{function_type = () -> (), sym_name = "basic_arrays_program"}> ({
    %0 = "arith.constant"() <{value = 10 : i32}> : () -> i32
    %1 = "arith.constant"() <{value = 20 : i32}> : () -> i32
    %2 = "tensor.from_elements"(%0, %1) : (i32, i32) -> tensor<2xi32>
    %3 = "arith.constant"() <{value = 5.500000e+00 : f32}> : () -> f32
    %4 = "arith.constant"() <{value = 1.400000e+00 : f32}> : () -> f32
    %5 = "tensor.from_elements"(%3, %4) : (f32, f32) -> tensor<2xf32>
    %6 = "arith.constant"() <{value = 1 : index}> : () -> index
    %7 = "tensor.extract"(%2, %6) : (tensor<2xi32>, index) -> i32
    %8 = "arith.constant"() <{value = 1 : i32}> : () -> i32
    %9 = "arith.index_cast"(%8) : (i32) -> index
    %10 = "tensor.extract"(%5, %9) : (tensor<2xf32>, index) -> f32
    "qnet.return"() : () -> ()
  }) : () -> ()
}) : () -> ()
"""
        assert str(module.generic_asm) == expected_generic_asm

    @pytest.mark.skip(reason="Mutation of the size of the array is not yet implemented")
    def test_arrays_with_mutation_program_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = array_with_mutation_program.module
        assert str(ex.value) == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        _, module = array_with_mutation_program.compile()
        assert isinstance(module, QoalaModule)
        expected_asm = """module {
  qnet.func @array_with_mutation_program() {
    %c10_i32 = arith.constant 10 : i32
    %c20_i32 = arith.constant 20 : i32
    %from_elements = tensor.from_elements %c10_i32, %c20_i32 : tensor<2xi32>
    %cst = arith.constant 5.500000e+00 : f32
    %cst_0 = arith.constant 1.400000e+00 : f32
    %from_elements_1 = tensor.from_elements %cst, %cst_0 : tensor<2xf32>
    ;; TODO - Mutation not supported yet
    qnet.return
  }
}
"""
        assert str(module.asm) == expected_asm
