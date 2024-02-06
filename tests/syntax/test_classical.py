import pytest

from qoala.types.classical.integer import Int32


class TestClassicalSyntax:
    def test_int32_creation(self):
        value_a = Int32(0)
        assert isinstance(value_a, Int32)
        #assert value_a.get_value() == 0

    def test_int32_creation_from_other_int32(self):
        value_a = Int32(immediate=10)
        value_b = Int32(other_int32=value_a)
        assert isinstance(value_b, Int32)
        #assert value_b.get_value() == 10

    @pytest.mark.skip(reason="Overloaded operators do not return anything just yet")
    def test_int32_operator_overload_correctness(self):
        value_a = Int32(immediate=2)
        value_b = Int32(immediate=6)
        value_c = value_a + value_b
        value_d = value_b + value_a
        value_e = value_b - value_a
        value_f = value_a - value_b
        value_g = value_a * value_b
        value_h = value_b * value_a
        value_i = value_b / value_a
        value_j = value_a / value_b

        # Assert closure correctness
        assert isinstance(value_c, Int32)
        assert isinstance(value_d, Int32)
        assert isinstance(value_e, Int32)
        assert isinstance(value_f, Int32)
        assert isinstance(value_g, Int32)
        assert isinstance(value_h, Int32)
        assert isinstance(value_i, Int32)
        assert isinstance(value_j, Int32)

        # Assert operation application correcteness
        #assert value_c.get_value() == 8
        #assert value_d.get_value() == 8
        #assert value_e.get_value() == 4
        #assert value_f.get_value() == -4
        #assert value_g.get_value() == 12
        #assert value_h.get_value() == 12
        #assert value_i.get_value() == 3
        #assert value_j.get_value() == 0
