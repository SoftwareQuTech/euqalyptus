import pytest
from inspect import getsourcelines
from sys import version_info
from pathlib import Path

from euqalyptus import QoalaProgram, QoalaModule
from euqalyptus.errors import NotYetCompiledError
from euqalyptus.operations import Remote
from euqalyptus.operations.communication import recv_floats
from euqalyptus.types.quantum import Entangle


# It is possible to move this whole function around, and tests will not break
# However, if you add lines in between the body, the assertions in the tests below will break.
@QoalaProgram
def quantum_entanglement_program_b():
    Remote("Bob")
    q0, q1, q2 = Entangle("Bob", 3)
    t1 = recv_floats("Bob", 2)
    q2.rot_X(angle=t1[0])
    t2 = recv_floats("Bob", 2)
    q2.rot_Y(angle=t2[1])
    m = q2.measure()


class TestQoalaQnetPythonBindingsQuantumFragile:
    # The results of these tests are very fragile, since the asserted locations will change when
    # inserting more code above here
    def test_entanglement_program_b_to_qoala_qnet(self):
        with pytest.raises(NotYetCompiledError) as ex:
            _, _ = quantum_entanglement_program_b.module
        assert (
            str(ex.value)
            == "The program has not been compiled yet. Did you invoke 'compile()' on it?"
        )
        _, module = quantum_entanglement_program_b.compile()
        assert isinstance(module, QoalaModule)
        # NOTE - All the qubit operations performed on a qubit modify the internal state of the qubit,
        #        as seen from the SDK side of the compiler. However, the semantics of the generated MLIR
        #        is a bit different. Since MLIR follows a Single Static Assignment (SSA) approach, an
        #        operation _cannot_ modify the state of a registry, but rather _returns_ the modified
        #        value, so it can be assigned to a new registry.
        #        Being this said, successive operations applied on the same qubit (as depicted in the
        #        code tested in this case) _MUST_ operate on the "updated" value of the qubit.
        expected_asm = """module {
  qnet.remote @Bob
  qnet.func @quantum_entanglement_program_b() {
    %0 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %1 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %2 = qnet.eprs  {remote = @Bob} : !qnet.qubit
    %3 = qnet.recv_floats  {length = 2 : i32, remote = @Bob} : tensor<2xf32>
    %c0 = arith.constant 0 : index
    %extracted = tensor.extract %3[%c0] : tensor<2xf32>
    %4 = qnet.rot_x %2, %extracted : !qnet.qubit
    %5 = qnet.recv_floats  {length = 2 : i32, remote = @Bob} : tensor<2xf32>
    %c1 = arith.constant 1 : index
    %extracted_0 = tensor.extract %5[%c1] : tensor<2xf32>
    %6 = qnet.rot_y %4, %extracted_0 : !qnet.qubit
    %7 = qnet.measure %6 : i1
    qnet.return
  }
}
"""
        current_path: Path = Path(__file__).resolve()  # type: ignore[annotation-unchecked]
        _, line_no = getsourcelines(quantum_entanglement_program_b._entry_fun)
        assert str(module.asm) == expected_asm
        expected_dbg_asm_a = f"""module {{
  qnet.remote @Bob loc(#loc1)
  qnet.func @quantum_entanglement_program_b() {{
    %0 = qnet.eprs  {{remote = @Bob}} : !qnet.qubit loc(#loc2)
    %1 = qnet.eprs  {{remote = @Bob}} : !qnet.qubit loc(#loc2)
    %2 = qnet.eprs  {{remote = @Bob}} : !qnet.qubit loc(#loc2)
    %3 = qnet.recv_floats  {{length = 2 : i32, remote = @Bob}} : tensor<2xf32> loc(#loc3)
    %c0 = arith.constant 0 : index loc(#loc3)
    %extracted = tensor.extract %3[%c0] : tensor<2xf32> loc(#loc4)
    %4 = qnet.rot_x %2, %extracted : !qnet.qubit loc(#loc5)
    %5 = qnet.recv_floats  {{length = 2 : i32, remote = @Bob}} : tensor<2xf32> loc(#loc6)
    %c1 = arith.constant 1 : index loc(#loc6)
    %extracted_0 = tensor.extract %5[%c1] : tensor<2xf32> loc(#loc7)
    %6 = qnet.rot_y %4, %extracted_0 : !qnet.qubit loc(#loc8)
    %7 = qnet.measure %6 : i1 loc(#loc9)
    qnet.return loc(#loc)
  }} loc(#loc)
}} loc(#loc)
#loc = loc("{str(current_path)}":{line_no}:0)
#loc1 = loc("{str(current_path)}":{line_no + 2}:4)
#loc2 = loc("{str(current_path)}":{line_no + 3}:17)
#loc3 = loc("{str(current_path)}":{line_no + 4}:9)
#loc4 = loc("{str(current_path)}":{line_no + 5}:19)
#loc5 = loc("{str(current_path)}":{line_no + 5}:4)
#loc6 = loc("{str(current_path)}":{line_no + 6}:9)
#loc7 = loc("{str(current_path)}":{line_no + 7}:19)
#loc8 = loc("{str(current_path)}":{line_no + 7}:4)
#loc9 = loc("{str(current_path)}":{line_no + 8}:8)
"""
        expected_dbg_asm_b = f"""module {{
  qnet.remote @Bob loc(#loc1)
  qnet.func @quantum_entanglement_program_b() {{
    %0 = qnet.eprs  {{remote = @Bob}} : !qnet.qubit loc(#loc2)
    %1 = qnet.eprs  {{remote = @Bob}} : !qnet.qubit loc(#loc2)
    %2 = qnet.eprs  {{remote = @Bob}} : !qnet.qubit loc(#loc2)
    %3 = qnet.recv_floats  {{length = 2 : i32, remote = @Bob}} : tensor<2xf32> loc(#loc3)
    %c0 = arith.constant 0 : index loc(#loc3)
    %extracted = tensor.extract %3[%c0] : tensor<2xf32> loc(#loc4)
    %4 = qnet.rot_x %2, %extracted : !qnet.qubit loc(#loc4)
    %5 = qnet.recv_floats  {{length = 2 : i32, remote = @Bob}} : tensor<2xf32> loc(#loc5)
    %c1 = arith.constant 1 : index loc(#loc5)
    %extracted_0 = tensor.extract %5[%c1] : tensor<2xf32> loc(#loc6)
    %6 = qnet.rot_y %4, %extracted_0 : !qnet.qubit loc(#loc6)
    %7 = qnet.measure %6 : i1 loc(#loc7)
    qnet.return loc(#loc)
  }} loc(#loc)
}} loc(#loc)
#loc = loc("{str(current_path)}":{line_no}:0)
#loc1 = loc("{str(current_path)}":{line_no + 2}:0)
#loc2 = loc("{str(current_path)}":{line_no + 3}:0)
#loc3 = loc("{str(current_path)}":{line_no + 4}:0)
#loc4 = loc("{str(current_path)}":{line_no + 5}:0)
#loc5 = loc("{str(current_path)}":{line_no + 6}:0)
#loc6 = loc("{str(current_path)}":{line_no + 7}:0)
#loc7 = loc("{str(current_path)}":{line_no + 8}:0)
"""
        if version_info.minor >= 11:
            assert str(module.asm_dbg) == expected_dbg_asm_a
        else:
            # In python 3.10, we don't have information about the column
            assert str(module.asm_dbg) == expected_dbg_asm_b
