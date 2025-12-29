from qoala.types.classical import QoalaClassicalType, _BooleanOperandsOverload


class QoalaBooleanType(
    QoalaClassicalType[bool], _BooleanOperandsOverload
):
    pass