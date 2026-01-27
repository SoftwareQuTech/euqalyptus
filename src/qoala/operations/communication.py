from typing import List

from qoala.ast.model import QoalaRuntimeValue
from qoala.ast.operations import QoalaOperation
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
from qoala.types.classical import IntArray, FloatArray, ScopedVar
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
        cls,
        remote_name: Remote | str,
        *args: IntArray | QoalaIntegerType | QoalaRuntimeValue | int,
    ):
        assert isinstance(remote_name, (DeclaredRemote, str))
        processed_args: List[
            QoalaInteger
            | QoalaRuntimeValue
            | QoalaOperation
            | QoalaBit
            | QoalaArray[QoalaInteger, int]
            | int
        ] = []
        for arg in args:
            assert isinstance(
                arg,
                (
                    QoalaInteger,
                    QoalaBit,
                    QoalaArray,
                    QoalaRuntimeValue,
                    QoalaOperation,
                    int,
                ),
            )
            if isinstance(arg, (QoalaRuntimeValue, QoalaOperation)):
                assert arg.can_evaluate_to(QoalaInteger) or arg.can_evaluate_to(
                    QoalaBit
                )
            processed_args.append(arg)
        return SendIntsOp(*processed_args, remote_name=remote_name)

    def __init__(
        self,
        remote_name: Remote | str,
        *args: IntArray | QoalaIntegerType | ScopedVar | int,
    ):
        # Nothing to do here
        pass


# TODO - Inherit from what?
class SendFloats:
    def __new__(
        cls,
        remote_name: Remote | str,
        *args: FloatArray
        | QoalaFloatingPointType
        | QoalaIntegerType
        | QoalaRuntimeValue
        | float,
    ):
        assert isinstance(remote_name, (DeclaredRemote, str))
        processed_args: List[
            QoalaInteger
            | QoalaRuntimeValue
            | QoalaOperation
            | QoalaBit
            | QoalaArray[QoalaFloat, float]
            | float
        ] = []
        for arg in args:
            assert isinstance(
                arg,
                (
                    QoalaInteger,
                    QoalaBit,
                    QoalaArray,
                    QoalaRuntimeValue,
                    QoalaOperation,
                    float,
                ),
            )
            if isinstance(arg, (QoalaRuntimeValue, QoalaOperation)):
                assert (
                    arg.can_evaluate_to(QoalaFloat)
                    or arg.can_evaluate_to(QoalaInteger)
                    or arg.can_evaluate_to(QoalaBit)
                )
            processed_args.append(arg)
        return SendFloatsOp(*processed_args, remote_name=remote_name)

    def __init__(
        self,
        remote_name: Remote | str,
        *args: FloatArray
        | QoalaFloatingPointType
        | QoalaIntegerType
        | ScopedVar
        | float,
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
