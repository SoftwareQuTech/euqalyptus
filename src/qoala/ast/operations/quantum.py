from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

import qnet.dialects.qnet as qnet
import qnet.dialects.tensor as tensor
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast.errors import OperationNotYetImplementedError
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.arrays import GetItem
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import QoalaExpression, QoalaFloatOrExpression, QoalaBit, QoalaInteger, QoalaArray, \
    QoalaNumericValue
from qoala.utils.binding_types import i32


@dataclass(init=False)
class QubitMeasure(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaBit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # TODO - Do we need tomake a difference between "qnet.measure" and "qnet.eprs_measure"??
        self.ir = qnet.measure(qin0=self.qubit.ir)
        return self.ir


@dataclass(init=False)
class QubitReset(QoalaOperation, ABC):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        # "void" operation; can always evaluate to anything
        return True

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(QubitReset.__name__)


@dataclass(init=False)
class XGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(XGate.__name__)


@dataclass(init=False)
class YGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(YGate.__name__)


@dataclass(init=False)
class ZGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(ZGate.__name__)


@dataclass(init=False)
class TGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(TGate.__name__)


@dataclass(init=False)
class HGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        self.ir = qnet.hadamard(self.qubit)
        return self.ir


@dataclass(init=False)
class KGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(KGate.__name__)


@dataclass(init=False)
class SGate(QoalaOperation):
    qubit: QoalaQubit

    def __init__(self, *operands: QoalaExpression):
        super().__init__()
        assert len(operands) == 1
        assert isinstance(operands[0], QoalaQubit)
        self.qubit = operands[0]
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(SGate.__name__)


class RotateBaseAxis(Enum):
    X = auto()
    Y = auto()
    Z = auto()


@dataclass(init=False)
class Rotate(QoalaOperation, ABC):
    qubit: QoalaQubit
    angle: QoalaFloatOrExpression

    def __init__(
            self,
            qubit: QoalaExpression,
            angle: QoalaFloatOrExpression,
            axis: RotateBaseAxis
    ):
        super().__init__()
        # We assume the users of this class will pass _at least_ default values for all operands
        assert isinstance(qubit, QoalaQubit)
        self.qubit = qubit
        self.angle = angle
        QoalaProgram.add_to_body(self)


@dataclass(init=False)
class RotateX(Rotate):
    def __init__(
            self,
            qubit: QoalaExpression,
            angle: QoalaFloatOrExpression
    ):
        super().__init__(qubit=qubit, angle=angle, axis=RotateBaseAxis.X)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # We first add this operation to the program
        self.ir = qnet.rot_x(qin=self.qubit.ir, angle=self.angle.ir)
        # We then register that the qubit has a "new" value
        self.qubit.ir = self.ir
        return self.ir


@dataclass(init=False)
class RotateY(Rotate):
    def __init__(
            self,
            qubit: QoalaExpression,
            angle: QoalaFloatOrExpression
    ):
        super().__init__(qubit=qubit, angle=angle, axis=RotateBaseAxis.Y)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # We first add this operation to the program
        self.ir = qnet.rot_y(qin=self.qubit.ir, angle=self.angle.ir)
        # We then register that the qubit has a "new" value
        self.qubit.ir = self.ir
        return self.ir


@dataclass(init=False)
class RotateZ(Rotate):
    def __init__(
            self,
            qubit: QoalaExpression,
            angle: QoalaFloatOrExpression
    ):
        super().__init__(qubit=qubit, angle=angle, axis=RotateBaseAxis.Z)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # We first add this operation to the program
        self.ir = qnet.rot_z(qin=self.qubit.ir, angle=self.angle.ir)
        # We then register that the qubit has a "new" value
        self.qubit.ir = self.ir
        return self.ir


@dataclass(init=False)
class CNotGate(QoalaOperation):
    quibit: QoalaQubit
    target: QoalaQubit

    def __init__(self, qubit: QoalaExpression, target: QoalaExpression):
        super().__init__()
        assert isinstance(qubit, QoalaQubit)
        assert isinstance(target, QoalaQubit)
        self.target = target
        self.qubit = qubit
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        # We first add this operation to the program
        self.ir = qnet.cnot(qin0=self.qubit.ir, qin1=self.target.ir)
        # We then register that the qubit has a "new" value
        self.qubit.ir = self.ir[0]
        self.target.ir = self.ir[1]
        return self.ir


@dataclass(init=False)
class CPhaseGate(QoalaOperation):
    target: QoalaQubit

    def __init__(self, target: QoalaExpression):
        super().__init__()
        assert isinstance(target, QoalaQubit)
        self.target = target
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaQubit:
            return True
        else:
            return False

    def to_ir(self, ctx: Context):
        raise OperationNotYetImplementedError(CPhaseGate.__name__)


@dataclass(init=False)
class RecvIntsOp(QoalaArray[QoalaInteger, int]):
    # Does this need to be a string? It seems to be just a "reference"
    remote: str

    def __init__(self, remote_name: str, length: int):
        super().__init__(base_size=32, base_type=int, length=length)
        self.remote = remote_name
        if length == 1:
            pass
        # We don't need to add this operation to the body, since it will be done
        # by the constructor of the parent class.

    def can_evaluate_to(self, cls):
        return cls == QoalaInteger

    def to_ir(self, ctx: Context):
        tensor_shape = tensor.RankedTensorType.get(shape=[self.length], element_type=i32())
        self.ir = qnet.recv_ints(remote=self.remote, cout=tensor_shape)
        if self.length == 1:
            # A tricky case. We need to insert operations to manually get the only
            # qubit of this entanglement pair
            # We need the index 0
            index = QoalaNumericValue.from_immediate(0, True)
            # We generate the IR of this index.
            index.to_ir(ctx)
            # We insert the GetItem operation
            extract = GetItem(self, index)
            # The IR of that operation is the "value of this operation"
            self.ir = extract.to_ir(ctx)

        return self.ir
