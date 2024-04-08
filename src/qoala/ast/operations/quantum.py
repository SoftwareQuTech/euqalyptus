from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Type, TypeVar

import qnet.dialects.qnet as qnet
import qnet.dialects.tensor as tensor
from qnet.ir import Context

from qoala import QoalaProgram
from qoala.ast.errors import OperationNotYetImplementedError, UnknownTypeError
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.arrays import GetItem
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import (
    QoalaExpression, QoalaFloatOrExpression, QoalaBit,
    QoalaInteger, QoalaFloat, QoalaArray, QoalaNumericValue
)
from qoala.utils.binding_types import i32, f32


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
        self.ir = qnet.measure(qin=self.qubit.ir)
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
        return cls == QoalaQubit

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
        return cls == QoalaQubit

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
        return cls == QoalaQubit

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
class DeclareRemote(QoalaOperation):
    remote_name: str

    def __init__(self, remote_name: str):
        super().__init__()
        self.remote_name = remote_name
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        return False

    def to_ir(self, ctx: Context):
        self.ir = qnet.remote(self.remote_name)
        return self.ir


_Qoala_Base_Type = TypeVar("_Qoala_Base_Type")
_Native_Base_Type = TypeVar("_Native_Base_Type")


@dataclass(init=False)
class BaseRecvOp(QoalaArray[_Qoala_Base_Type, _Native_Base_Type]):
    # Does this need to be a string? It seems to be just a "reference"
    remote: DeclareRemote | str
    base_type: Type

    def __init__(self, remote_name: DeclareRemote | str, length: int, base_type: Type):
        super().__init__(base_size=32, base_type=base_type, length=length)
        self.remote = remote_name
        self.base_type = base_type
        # We don't need to add this operation to the body, since it will be done
        # by the constructor of the parent class.

    def can_evaluate_to(self, cls):
        if self.length == 1:
            if self.base_type == int:
                return cls == QoalaInteger
            elif self.base_type == float:
                return cls == QoalaFloat
            else:
                raise UnknownTypeError(f"Recv with base type '{self.base_type} cannot evaluate to '{cls}")
        else:
            return cls == QoalaArray

    def to_ir(self, ctx: Context):
        base_tensor_type = i32() if self.base_type == int else f32()
        tensor_shape = tensor.RankedTensorType.get(shape=[self.length], element_type=base_tensor_type)
        if isinstance(self.remote, DeclareRemote):
            remote_name = self.remote.remote_name
        else:
            remote_name = self.remote
        if self.base_type == int:
            self.ir = qnet.recv_ints(remote=remote_name, cout=tensor_shape)
        elif self.base_type == float:
            self.ir = qnet.recv_floats(remote=remote_name, cout=tensor_shape)
        else:
            raise UnknownTypeError(f"Cannot create recv operation for base type '{self.base_type}'")
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


@dataclass(init=False)
class RecvIntsOp(BaseRecvOp[QoalaInteger, int]):
    def __init__(self, remote_name: DeclareRemote | str, length: int):
        super().__init__(remote_name=remote_name, length=length, base_type=int)


@dataclass(init=False)
class RecvFloatsOp(BaseRecvOp[QoalaFloat, float]):
    def __init__(self, remote_name: DeclareRemote | str, length: int):
        super().__init__(remote_name=remote_name, length=length, base_type=float)


@dataclass(init=False)
class BaseSendOp(QoalaOperation):
    remote: DeclareRemote | str
    values: List[QoalaExpression]
    base_type: Type
    qoala_type: Type

    def __init__(self, *vals: QoalaExpression, remote_name: str, base_type: Type, qoala_type: Type):
        super().__init__()
        self.remote = remote_name
        self.base_type = base_type
        self.values = []
        for val in vals:
            # TODO - Check if the value can evaluate to an array (tensor is already defined)
            # TODO - Think what happens if we mix single values and an array... flatmap?
            if isinstance(val, QoalaArray):
                # If the argument is an array, we will simply "open" the array...
                # If an already-packed array is the ONLY argument, this wastefully creates a new tensor
                # This is generic enough to support mixed arrays and other values, but it's the bes we can do so far
                [self.values.append(array_val) for array_val in val.members]
                continue
            elif isinstance(val, base_type):
                val_to_add = QoalaNumericValue.from_immediate(val)
            elif val.can_evaluate_to(qoala_type):
                val_to_add = val
            else:
                raise UnknownTypeError(f"Send operation: value '{val}' cannot be converted to '{self.base_type}'")
            self.values.append(val_to_add)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return False

    def to_ir(self, ctx: Context):
        elements = [value.ir for value in self.values]
        if self.base_type is int:
            hir_base_type = i32()
        elif self.base_type is float:
            hir_base_type = f32()
        else:
            raise UnknownTypeError(f"Base type '{self.base_type.__name__}' for arrays is not supported")
        tensor_shape = tensor.RankedTensorType.get(shape=[len(elements)], element_type=hir_base_type)
        tensor_values = tensor.from_elements(elements=elements, result=tensor_shape)

        if isinstance(self.remote, DeclareRemote):
            remote_name = self.remote.remote_name
        else:
            remote_name = self.remote
        if self.base_type == int:
            self.ir = qnet.send_ints(cin=tensor_values, remote=remote_name)
        elif self.base_type == float:
            self.ir = qnet.send_floats(cin=tensor_values, remote=remote_name)
        else:
            raise UnknownTypeError(f"Cannot create send operation for base type '{self.base_type}'")
        return self.ir


@dataclass(init=False)
class SendIntsOp(BaseSendOp):
    def __init__(self, *vals: QoalaExpression, remote_name: DeclareRemote | str):
        super().__init__(*vals, remote_name=remote_name, qoala_type=QoalaInteger, base_type=int)


@dataclass(init=False)
class SendFloatsOp(BaseSendOp):
    def __init__(self, *vals: QoalaExpression, remote_name: DeclareRemote | str):
        super().__init__(*vals, remote_name=remote_name, qoala_type=QoalaFloat, base_type=float)
