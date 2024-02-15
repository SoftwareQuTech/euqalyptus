from qoala.ast.operations.numeric import Add, Subtract, Multiply, Divide
from qoala.ast.value import QoalaInteger, Signedness
from qoala.types.classical.integer import Int32


class TestIntegerSemantics:
    def test_basic_integers(self):
        int_a = Int32(10)
        int_b = Int32(20)
        int_c = int_a + int_b
        int_d = int_a - int_b
        int_e = int_a * int_b
        int_f = int_a / int_b

        # From the syntax tests, we know that all the statements above
        # Return a QoalaExpression. We now want to test for the specific
        # type and the content within it
        assert isinstance(int_a, QoalaInteger)
        assert isinstance(int_b, QoalaInteger)
        assert isinstance(int_c, Add)
        assert isinstance(int_d, Subtract)
        assert isinstance(int_e, Multiply)
        assert isinstance(int_f, Divide)

        assert int_a.width == 32
        assert int_a.signedness == Signedness.SIGNED
        assert int_a.value == 10

        assert int_b.width == 32
        assert int_b.signedness == Signedness.SIGNED
        assert int_b.value == 20

        assert int_c.operand_a == int_a
        assert int_c.operand_b == int_b

        assert int_d.operand_a == int_a
        assert int_d.operand_b == int_b

        assert int_e.operand_a == int_a
        assert int_e.operand_b == int_b

        assert int_f.operand_a == int_a
        assert int_f.operand_b == int_b
