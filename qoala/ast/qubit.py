from typing import Self

from qoala.ast.value import QoalaBit, QoalaInteger, QoalaFloat


class QoalaQubit:
    pass


class QoalaLocalQubit(QoalaQubit):
    def measure(self) -> QoalaBit:
        # TODO - Implement: Modify the dummy object returned
        return QoalaBit()

    def X(self):
        # TODO - Implement
        pass

    def Y(self):
        # TODO - Implement
        pass

    def Z(self):
        # TODO - Implement
        pass

    def T(self):
        # TODO - Implement
        pass

    def H(self):
        # TODO - Implement
        pass

    def K(self):
        # TODO - Implement
        pass

    def S(self):
        # TODO - Implement
        pass

    def rot_X(
            self,
            n: int | QoalaInteger = 0,
            d: int | QoalaInteger = 0,
            angle: float | QoalaFloat | None = None
    ):
        # TODO - Implement
        pass

    def rot_Y(
            self,
            n: int | QoalaInteger = 0,
            d: int | QoalaInteger = 0,
            angle: float | QoalaFloat | None = None
    ):
        # TODO - Implement
        pass

    def rot_Z(
            self,
            n: int | QoalaInteger = 0,
            d: int | QoalaInteger = 0,
            angle: float | QoalaFloat | None = None
    ):
        # TODO - Implement
        pass

    def cnot(self, target: Self) -> None:
        # TODO - Implement
        pass

    def cphase(self, target: Self) -> None:
        # TODO - Implement
        pass

    def reset(self) -> None:
        # TODO - Implement
        pass

    def free(self) -> None:
        # TODO - Implement
        pass


# TODO - Implement remote qubits
class QoalaRemoteQubit(QoalaQubit):
    pass
