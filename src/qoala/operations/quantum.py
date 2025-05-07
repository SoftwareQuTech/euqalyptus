from qoala.ast.operations.quantum import (
    RecvIntsOp,
    RecvFloatsOp,
    SendIntsOp,
    SendFloatsOp,
)
from qoala.operations import Remote
from qoala.types.classical import IntArray, FloatArray
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.integer import QoalaIntegerType


class RecvInts(IntArray):

    def __new__(cls, remote_name: Remote | str, length: int):
        return RecvIntsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvInt(RecvInts, QoalaIntegerType):

    def __new__(cls, remote_name: Remote | str, length: int = 1):
        return RecvIntsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int = 1):
        # Nothing to do here
        super().__init__(remote_name=remote_name, length=length)


class RecvFloats(FloatArray):

    def __new__(cls, remote_name: Remote | str, length: int):
        return RecvFloatsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvFloat(RecvFloats, QoalaFloatingPointType):

    def __new__(cls, remote_name: Remote | str):
        return RecvFloatsOp(remote_name=remote_name, length=1)

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        super().__init__(remote_name=remote_name, length=1)


# TODO - Inherit from what?
class SendInts:

    def __new__(
        cls, remote_name: Remote | str, *args: IntArray | QoalaIntegerType | int
    ):
        return SendIntsOp(*args, remote_name=remote_name)

    def __init__(
        self, remote_name: Remote | str, *args: IntArray | QoalaIntegerType | int
    ):
        # Nothing to do here
        pass


# TODO - Inherit from what?
class SendFloats:

    def __new__(
        cls,
        remote_name: Remote | str,
        *args: FloatArray | QoalaFloatingPointType | float,
    ):
        return SendFloatsOp(*args, remote_name=remote_name)

    def __init__(
        self,
        remote_name: Remote | str,
        *args: FloatArray | QoalaFloatingPointType | float,
    ):
        # Nothing to do here
        pass


recv_int = RecvInt
recv_ints = RecvInts
recv_float = RecvFloat
recv_floats = RecvFloats
send_int = SendInts
send_ints = SendInts
send_float = SendFloats
send_floats = SendFloats
