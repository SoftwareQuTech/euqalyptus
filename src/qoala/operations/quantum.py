from qoala.ast.operations.quantum import RecvIntsOp, RecvFloatsOp
from qoala.operations import Remote
from qoala.types.classical.arrays import IntArray, FloatArray
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.integer import QoalaIntegerType


class RecvInts(IntArray):
    def __new__(cls, remote_name: Remote | str, length: int, *args, **kwargs):
        return RecvIntsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvInt(RecvInts, QoalaIntegerType):
    def __new__(cls, remote_name: Remote | str, *args, **kwargs):
        return RecvIntsOp(remote_name=remote_name, length=1)

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        super().__init__(remote_name=remote_name, length=1)


class RecvFloats(FloatArray):
    def __new__(cls, remote_name: Remote | str, length: int, *args, **kwargs):
        return RecvFloatsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvFloat(RecvFloats, QoalaFloatingPointType):
    def __new__(cls, remote_name: Remote | str, *args, **kwargs):
        return RecvFloatsOp(remote_name=remote_name, length=1)

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        super().__init__(remote_name=remote_name, length=1)


# TODO - Inherit from what?
class SendInts:
    def __new__(cls, remote_name: Remote | str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        pass


# TODO - Inherit from what?
class SendFloats:
    def __new__(cls, remote_name: Remote | str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        pass


recv_int = RecvInt
recv_ints = RecvInts
recv_float = RecvFloat
recv_floats = RecvFloats
send_int = RecvInt
send_float = RecvFloat
