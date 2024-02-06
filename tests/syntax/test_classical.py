import pytest

from typing import Generic, TypeVar

from qoala.types.classical.integer import Int32, UInt32, Int, IntegerType

_Type = TypeVar("_Type", bound=IntegerType)


@pytest.mark.parametrize("clazz", (Int32, UInt32, Int))
class TestClassicalSyntax(Generic[_Type]):
    # These two methods are helpful to create the right type of integer, by
    # _statically_ calling the constructor depending on the name of the class.
    # It deviates a bit from what a user could write (a user will never use a
    # factory based on a parametric type), but it simplifies the specification
    # of all the possible test cases.

    @staticmethod
    def _get_int_from_immediate(clazz: type, immediate: int) -> _Type:
        match clazz.__name__:
            case "Int32":
                return Int32(immediate=immediate)
            case "UInt32":
                return UInt32(immediate=immediate)
            case "Int":
                return Int(immediate=immediate)
            case _:
                raise NotImplementedError()

    @staticmethod
    def _get_int_from_same_type(clazz: type, other_int: _Type) -> _Type:
        match clazz.__name__:
            case "Int32":
                return Int32(other_int32=other_int)
            case "UInt32":
                return UInt32(other_uint32=other_int)
            case "Int":
                return Int(other_int32=other_int)
            case _:
                raise NotImplementedError()

    def test_int_creation(self, clazz: type):
        value_a = TestClassicalSyntax._get_int_from_immediate(clazz, 0)
        assert isinstance(value_a, clazz)
        #assert value_a.get_value() == 0

    def test_int_creation_from_other_int32(self, clazz: type):
        value_a = TestClassicalSyntax._get_int_from_immediate(clazz, 10)
        value_b = TestClassicalSyntax._get_int_from_same_type(clazz, value_a)
        assert isinstance(value_b, clazz)
        #assert value_b.get_value() == 10

    @pytest.mark.skip(reason="Int32 - Overloaded operators do not return anything just yet")
    def test_int_operator_overload_correctness(self, clazz: type):
        value_a = TestClassicalSyntax._get_int_from_immediate(clazz, 2)
        value_b = TestClassicalSyntax._get_int_from_immediate(clazz, 6)
        value_c = value_a + value_b
        value_d = value_b + value_a
        value_e = value_b - value_a
        value_f = value_a - value_b
        value_g = value_a * value_b
        value_h = value_b * value_a
        value_i = value_b / value_a
        value_j = value_a / value_b

        # Assert closure correctness
        assert isinstance(value_c, clazz)
        assert isinstance(value_d, clazz)
        assert isinstance(value_e, clazz)
        assert isinstance(value_f, clazz)
        assert isinstance(value_g, clazz)
        assert isinstance(value_h, clazz)
        assert isinstance(value_i, clazz)
        assert isinstance(value_j, clazz)

        # Assert operation application correctness
        #assert value_c.get_value() == 8
        #assert value_d.get_value() == 8
        #assert value_e.get_value() == 4
        #assert value_f.get_value() == -4
        #assert value_g.get_value() == 12
        #assert value_h.get_value() == 12
        #assert value_i.get_value() == 3
        #assert value_j.get_value() == 0
