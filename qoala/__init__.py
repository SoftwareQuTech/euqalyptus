from abc import ABC, abstractmethod
from typing import List, Any


class QoalaProgram(ABC):
    @abstractmethod
    def main(self, args: List[Any]) -> int:
        ...
