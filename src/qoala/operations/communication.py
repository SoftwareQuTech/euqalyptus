from typing import List

from qoala.ast.operations.communication import (
    RecvIntsOp,
    RecvFloatsOp,
    RecvIntOp,
    RecvFloatOp,
    SendIntsOp,
    SendFloatsOp,
    DeclaredRemote,
)
from qoala.ast.value import QoalaInteger, QoalaFloat, QoalaArray, QoalaBit
from qoala.operations import Remote
from qoala.types.classical import IntArray, FloatArray
from qoala.types.classical.floats import QoalaFloatingPointType
from qoala.types.classical.integer import QoalaIntegerType


class RecvInts(IntArray):
    def __new__(cls, remote_name: Remote | str, length: int):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvIntsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvInt(QoalaIntegerType):
    def __new__(cls, remote_name: Remote | str):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvIntOp(remote_name=remote_name)

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        pass


class RecvFloats(FloatArray):
    def __new__(cls, remote_name: Remote | str, length: int):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvFloatsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvFloat(QoalaFloatingPointType):
    def __new__(cls, remote_name: Remote | str):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvFloatOp(remote_name=remote_name)

    def __init__(self, remote_name: Remote | str):
        pass


# TODO - Inherit from what?
class SendInts:
    def __new__(
        cls, remote_name: Remote | str, *args: IntArray | QoalaIntegerType | int
    ):
        assert isinstance(remote_name, (DeclaredRemote, str))
        processed_args: List[
            QoalaInteger | QoalaBit | QoalaArray[QoalaInteger, int] | int
        ] = []
        for arg in args:
            assert isinstance(arg, (QoalaInteger, QoalaBit, QoalaArray, int))
            processed_args.append(arg)
        return SendIntsOp(*processed_args, remote_name=remote_name)

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
        *args: FloatArray | QoalaFloatingPointType | QoalaIntegerType | float,
    ):
        assert isinstance(remote_name, (DeclaredRemote, str))
        processed_args: List[
            QoalaInteger | QoalaBit | QoalaArray[QoalaFloat, float] | float
        ] = []
        for arg in args:
            assert isinstance(arg, (QoalaInteger, QoalaBit, QoalaArray, float))
            processed_args.append(arg)
        return SendFloatsOp(*processed_args, remote_name=remote_name)

    def __init__(
        self,
        remote_name: Remote | str,
        *args: FloatArray | QoalaFloatingPointType | QoalaIntegerType | float,
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
