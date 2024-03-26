from qoala.types.classical.integer import QoalaIntegerType
from qoala.types.classical.floats import QoalaFloatingPointType


class RecvInt(QoalaIntegerType):
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        pass


recv_int = RecvInt


class RecvFloat(QoalaFloatingPointType):
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        pass


recv_float = RecvFloat


# TODO - Inherit from what?
class SendInt:
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        pass


send_int = RecvInt


# TODO - Inherit from what?
class RecvFloat:
    def __new__(cls, remote_name: str, *args, **kwargs):
        # TODO
        pass

    def __init__(self, remote_name: str):
        # Nothing to do here
        pass


send_float = RecvFloat
