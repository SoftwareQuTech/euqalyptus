from qoala.ast import QoalaExpression
from qoala.types.classical.integer import Int32


# TODO - Re-think what we want to test here, and how
class TestIntegerSemantics:
    def test_basic_integer(self):
        int_a = Int32(10)
        int_b = Int32(20)
        int_c = int_a + int_b

        assert isinstance(int_a, QoalaExpression)
        assert isinstance(int_b, QoalaExpression)
        assert isinstance(int_c, QoalaExpression)
