from typing import List, Any

import pytest

from qoala import QoalaProgram, QoalaProgramBase
from qoala.errors import QuantumProgramNotImplementedError


class _EmptyQoalaProgramBase(QoalaProgramBase):

    def main(self, args: List[Any]) -> int:
        pass


class _IncompleteQoalaProgramBase(QoalaProgramBase):
    pass


class TestBase:

    def test_class_without_entry_point(self):
        with pytest.raises(QuantumProgramNotImplementedError) as exec_info:
            _ = _IncompleteQoalaProgramBase()
        assert len(exec_info.value.args) == 1
        assert isinstance(exec_info.value.args[0], str)
        assert (
            "Quantum program '_IncompleteQoalaProgramBase' cannot be instantiated. "
            "Main function was not found in the class '_IncompleteQoalaProgramBase'"
        ) in exec_info.value.args[0]

    def test_class_with_entry_point(self):
        program = _EmptyQoalaProgramBase()
        assert isinstance(program, QoalaProgram)
