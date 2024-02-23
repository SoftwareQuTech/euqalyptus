import pytest

from qoala import QoalaProgram
from typing import List, Any


class _EmptyQoalaProgram(QoalaProgram):
    def main(self, args: List[Any]) -> int:
        pass


class _IncompleteQoalaProgram(QoalaProgram):
    pass


class TestBase:
    def test_class_without_entry_point(self):
        with pytest.raises(TypeError) as exec_info:
            _ = _IncompleteQoalaProgram()
        assert len(exec_info.value.args) == 1
        assert isinstance(exec_info.value.args[0], str)
        assert "Can't instantiate abstract class" in exec_info.value.args[0]

    def test_class_with_entry_point(self):
        program = _EmptyQoalaProgram()
        assert isinstance(program, QoalaProgram)
