import math
from abc import ABC
from dataclasses import dataclass
from typing import List, Type, TypeVar

import qnet.dialects.qnet as qnet
import qnet.dialects.tensor as tensor
from qnet.extras.types import i32, f32
from qnet.ir import Context, Location, IntegerAttr

from qoala import QoalaProgram
from qoala.ast import checkbaseir, QoalaExpression
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.arrays import GetItem
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import (
    QoalaFloatOrExpression,
    QoalaInteger,
    QoalaFloat,
    QoalaArray,
    QoalaNumericValue,
    QoalaBit,
)
from qoala.errors import UnknownTypeError, UnknownRemoteError
from qoala.utils.debug_info import get_debug_info


@dataclass(init=False)
class _QubitBaseOperation(QoalaOperation, ABC):
    qubit: QoalaExpression

    def __init__(self, qubit: QoalaExpression):
        super().__init__()
        assert qubit.can_evaluate_to(QoalaQubit)
        self.debug_info = get_debug_info()
        self.qubit = qubit

    def can_evaluate_to(self, cls) -> bool:
        return cls == QoalaQubit


class QubitMeasure(_QubitBaseOperation, QoalaBit):

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        super().__init__(qubit=operands[0])
        QoalaProgram.add_to_body(self)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = qnet.measure(qin=self.qubit.ir_value, loc=source_location)


@dataclass(init=False)
class Rotate(_QubitBaseOperation, ABC):
    angle: QoalaFloatOrExpression

    def __init__(self, qubit: QoalaExpression, angle: QoalaFloatOrExpression):
        super().__init__(qubit=qubit)
        # We assume the users of this class will pass _at least_ default values for all operands
        self.angle = angle
        QoalaProgram.add_to_body(self)


class RotateX(Rotate):

    def __init__(self, qubit: QoalaExpression, angle: QoalaFloatOrExpression):
        super().__init__(qubit=qubit, angle=angle)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # We first add this operation to the program
        self.ir_value = qnet.rot_x(
            qin=self.qubit.ir_value, angle=self.angle.ir_value, loc=source_location
        )
        # We then register that the qubit has a "new" value
        self.qubit.ir_value = self.ir_value


class RotateY(Rotate):

    def __init__(self, qubit: QoalaExpression, angle: QoalaFloatOrExpression):
        super().__init__(qubit=qubit, angle=angle)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # We first add this operation to the program
        self.ir_value = qnet.rot_y(
            qin=self.qubit.ir_value, angle=self.angle.ir_value, loc=source_location
        )
        # We then register that the qubit has a "new" value
        self.qubit.ir_value = self.ir_value


class RotateZ(Rotate):

    def __init__(self, qubit: QoalaExpression, angle: QoalaFloatOrExpression):
        super().__init__(qubit=qubit, angle=angle)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # We first add this operation to the program
        self.ir_value = qnet.rot_z(
            qin=self.qubit.ir_value, angle=self.angle.ir_value, loc=source_location
        )
        # We then register that the qubit has a "new" value
        self.qubit.ir_value = self.ir_value


# Decorator used to "template" the classes annotated.
# This decorator will create a class that is a subclass of 'base_class' and
# that contains the '__init__' and 'compile' methods
def RotationAlias(base_clazz: Type, base_rotation: float):
    def outer(_):
        if not issubclass(base_clazz, Rotate):
            raise TypeError(
                "The 'RotationAlias' decorator can only be applied to subclasses of 'Rotation'"
            )

        class _BaseEasyRotation(base_clazz):

            def __init__(self, *operands: QoalaExpression):
                assert len(operands) == 1
                rotation_angle = QoalaNumericValue.from_immediate(
                    base_rotation, get_debug_info()
                )
                super().__init__(qubit=operands[0], angle=rotation_angle)

            @checkbaseir
            def compile(self, ctx: Context) -> None:
                super().compile(ctx)

        return _BaseEasyRotation

    return outer


# Definition of the "Rotation Aliases"; basic rotations with a fixed given angle
@RotationAlias(RotateX, base_rotation=math.pi)
class XGate:
    pass


@RotationAlias(RotateY, base_rotation=math.pi)
class YGate:
    pass


@RotationAlias(RotateZ, base_rotation=math.pi)
class ZGate:
    pass


@RotationAlias(RotateZ, base_rotation=math.pi / 2.0)
class SGate:
    pass


@RotationAlias(RotateZ, base_rotation=math.pi / 4.0)
class TGate:
    pass


class HGate(_QubitBaseOperation):

    def __init__(self, *operands: QoalaExpression):
        assert len(operands) == 1
        super().__init__(qubit=operands[0])
        QoalaProgram.add_to_body(self)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = qnet.hadamard(self.qubit.ir_value, loc=source_location)


@dataclass(init=False)
class CNotGate(_QubitBaseOperation):
    target: QoalaQubit

    def __init__(self, qubit: QoalaExpression, target: QoalaExpression):
        super().__init__(qubit=qubit)
        assert target.can_evaluate_to(QoalaQubit)
        self.target = target
        QoalaProgram.add_to_body(self)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # We first add this operation to the program
        self.ir_value = qnet.cnot(
            qin0=self.qubit.ir_value, qin1=self.target.ir_value, loc=source_location
        )
        # We then register that the qubit has a "new" value
        self.qubit.ir_value = self.ir_value[0]
        self.target.ir_value = self.ir_value[1]


@dataclass(init=False)
class CPhaseGate(_QubitBaseOperation):
    # This is an alias for the "CZ" gate
    target: QoalaExpression

    def __init__(self, qubit: QoalaExpression, target: QoalaExpression):
        super().__init__(qubit=qubit)
        assert target.can_evaluate_to(QoalaQubit)
        self.target = target
        QoalaProgram.add_to_body(self)

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        # We first add this operation to the program
        self.ir_value = qnet.cz(
            qin0=self.qubit.ir_value, qin1=self.target.ir_value, loc=source_location
        )
        # We then register that the qubit has a "new" value
        self.qubit.ir_value = self.ir_value[0]
        self.target.ir_value = self.ir_value[1]


@dataclass(init=False)
class DeclaredRemote(QoalaOperation):
    remote_name: str

    def __init__(self, remote_name: str):
        super().__init__()
        self.remote_name = remote_name
        QoalaProgram.add_declared_remote(remote_name, self)

    def can_evaluate_to(self, cls) -> bool:
        return False

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = qnet.remote(self.remote_name, loc=source_location)


_Qoala_Base_Type = TypeVar("_Qoala_Base_Type")
_Native_Base_Type = TypeVar("_Native_Base_Type")


@dataclass(init=False)
class BaseRecvOp(QoalaArray[_Qoala_Base_Type, _Native_Base_Type]):
    # Does this need to be a string? It seems to be just a "reference"
    remote: DeclaredRemote | str
    base_type: Type
    index_op: QoalaExpression | None
    get_op: QoalaExpression | None

    def __init__(self, remote_name: DeclaredRemote | str, length: int, base_type: Type):
        super().__init__(
            base_size=32, base_type=base_type, length=length, base_clone=None
        )
        self.remote = remote_name
        self.base_type = base_type
        self.index_op = None
        self.get_op = None
        if length == 1:
            # A tricky case. We need to insert operations to manually get the only
            # qubit of this entanglement pair
            # We need the index 0
            self.index_op = QoalaNumericValue.from_immediate(
                0, dbg_info=self.debug_info, is_index=True
            )
            # We insert the GetItem operation, we pass the debug info of the same item
            self.extract_op = GetItem(self, self.index_op, dbg_info=self.debug_info)
        # We don't need to add this operation to the body, since it will be done
        # by the constructor of the parent class.

    def can_evaluate_to(self, cls) -> bool:
        if self.length == 1:
            if self.base_type == int:
                return cls == QoalaInteger
            elif self.base_type == float:
                return cls == QoalaFloat
            else:
                raise UnknownTypeError(
                    f"Recv with base type '{self.base_type} cannot evaluate to '{cls}"
                )
        else:
            return cls == QoalaArray

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        base_tensor_type = i32() if self.base_type == int else f32()
        tensor_shape = tensor.RankedTensorType.get(
            shape=[self.length], element_type=base_tensor_type, loc=source_location
        )
        if isinstance(self.remote, DeclaredRemote):
            remote_name = self.remote.remote_name
        else:
            remote = QoalaProgram.get_declared_remote(self.remote)
            if remote is None:
                raise UnknownRemoteError(self.remote)
            remote_name = self.remote
        length_attr = IntegerAttr.get(i32(), self.length)
        if self.base_type == int:
            self.ir_value = qnet.recv_ints(
                remote=remote_name,
                cout=tensor_shape,
                length=length_attr,
                loc=source_location,
            )
        elif self.base_type == float:
            self.ir_value = qnet.recv_floats(
                remote=remote_name,
                cout=tensor_shape,
                length=length_attr,
                loc=source_location,
            )
        else:
            raise UnknownTypeError(
                f"Cannot create recv operation for base type '{self.base_type}'"
            )
        if self.length == 1:
            # In this case the IR of the Recv operation is the value of the extract operation
            self.index_op.compile(ctx)
            self.extract_op.compile(ctx)
            self.ir_value = self.extract_op.ir_value


@dataclass(init=False)
class RecvIntsOp(BaseRecvOp[QoalaInteger, int]):

    def __init__(self, remote_name: DeclaredRemote | str, length: int):
        super().__init__(remote_name=remote_name, length=length, base_type=int)


@dataclass(init=False)
class RecvFloatsOp(BaseRecvOp[QoalaFloat, float]):

    def __init__(self, remote_name: DeclaredRemote | str, length: int):
        super().__init__(remote_name=remote_name, length=length, base_type=float)


@dataclass(init=False)
class BaseSendOp(QoalaOperation):
    remote: DeclaredRemote | str
    values: List[QoalaExpression]
    base_type: Type
    qoala_type: Type

    def __init__(
        self,
        *vals: QoalaExpression,
        remote_name: str,
        base_type: Type,
        qoala_type: Type,
    ):
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
                _ = [self.values.append(array_val) for array_val in val.members]
                continue
            elif isinstance(val, base_type):
                val_to_add = QoalaNumericValue.from_immediate(val, self.debug_info)
            elif val.can_evaluate_to(qoala_type):
                val_to_add = val
            else:
                raise UnknownTypeError(
                    f"Send operation: value '{val}' cannot be converted to '{self.base_type}'"
                )
            self.values.append(val_to_add)
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return False

    @checkbaseir
    def compile(self, ctx: Context) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        elements = [value.ir_value for value in self.values]
        if self.base_type is int:
            hir_base_type = i32()
        elif self.base_type is float:
            hir_base_type = f32()
        else:
            raise UnknownTypeError(
                f"Base type '{self.base_type.__name__}' for arrays is not supported"
            )
        tensor_shape = tensor.RankedTensorType.get(
            shape=[len(elements)], element_type=hir_base_type, loc=source_location
        )
        tensor_values = tensor.from_elements(
            elements=elements, result=tensor_shape, loc=source_location
        )

        if isinstance(self.remote, DeclaredRemote):
            remote_name = self.remote.remote_name
        else:
            remote_name = self.remote
        if self.base_type == int:
            self.ir_value = qnet.send_ints(
                cin=tensor_values, remote=remote_name, loc=source_location
            )
        elif self.base_type == float:
            self.ir_value = qnet.send_floats(
                cin=tensor_values, remote=remote_name, loc=source_location
            )
        else:
            raise UnknownTypeError(
                f"Cannot create send operation for base type '{self.base_type}'"
            )


@dataclass(init=False)
class SendIntsOp(BaseSendOp):

    def __init__(self, *vals: QoalaExpression, remote_name: DeclaredRemote | str):
        super().__init__(
            *vals, remote_name=remote_name, qoala_type=QoalaInteger, base_type=int
        )


@dataclass(init=False)
class SendFloatsOp(BaseSendOp):

    def __init__(self, *vals: QoalaExpression, remote_name: DeclaredRemote | str):
        super().__init__(
            *vals, remote_name=remote_name, qoala_type=QoalaFloat, base_type=float
        )
