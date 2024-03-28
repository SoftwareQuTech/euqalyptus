from qoala.ast.operations.quantum import RecvIntsOp

from qoala.types.classical.integer import QoalaIntegerType
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.arrays import IntArray, FloatArray


class RecvInts(IntArray):
    def __new__(cls, remote_name: str, length: int, *args, **kwargs):
        return RecvIntsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: str, length: int):
        # Nothing to do here
        super().__init__()
        pass


class RecvInt(RecvInts, QoalaIntegerType):
    def __new__(cls, remote_name: str, *args, **kwargs):
        return RecvIntsOp(remote_name=remote_name, length=1)

    def __init__(self, remote_name: str):
        # Nothing to do here
        super().__init__(remote_name=remote_name, length=1)


class RecvFloats(FloatArray):
    def __new__(cls, remote_name: str, length: int, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str, length: int):
        # Nothing to do here
        super().__init__()


class RecvFloat(RecvFloats, QoalaFloatingPointType):
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        super().__init__(remote_name=remote_name, length=1)


# TODO - Inherit from what?
class SendInts:
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        pass


# TODO - Inherit from what?
class SendFloats:
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        pass


recv_int = RecvInt
recv_float = RecvFloat
send_int = RecvInt
send_float = RecvFloat
