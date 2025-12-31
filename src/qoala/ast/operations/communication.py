from dataclasses import dataclass
from typing import List, Type, TypeVar, Optional

import qnet.dialects.tensor as tensor
import qnet.dialects.qnet as qnet
from qnet.extras.types import i32, f32
from qnet.ir import Context, Location, IntegerAttr

from qoala import QoalaProgram
from qoala.ast import checkbaseir, QoalaExpression
from qoala.ast.value import QoalaReferenceInsideArray
from qoala.ast.operations import QoalaOperation
from qoala.ast.operations.arrays import GetItem
from qoala.ast.operations.casts import BitToInt, IntToFloat
from qoala.ast.operations.quantum import QubitMeasure
from qoala.ast.value import (
    QoalaInteger,
    QoalaFloat,
    QoalaArray,
    QoalaNumericValue,
)
from qoala.errors import (
    UnknownTypeError,
    UnknownRemoteError,
    ValueUnknownAtCompileTimeError,
)


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
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
        if length == 1 and not QoalaProgram.compile_singular_comm_ops():
            # A tricky case. We need to insert operations to manually get the only
            # value of this array... ONLY if we are not creating singular versions of this op
            # We need the index 0
            self.index_op = QoalaNumericValue.from_immediate(
                0, dbg_info=self.debug_info, is_index=True
            )
            # We insert the GetItem operation, we pass the debug info of the same item
            self.extract_op = GetItem(self, self.index_op, dbg_info=self.debug_info)
        # We don't need to add this operation to the body, since it will be done
        # by the constructor of the parent class.

    def __getitem__(self, item_index: QoalaExpression | int) -> QoalaExpression:
        if QoalaProgram.compile_singular_comm_ops():
            if not isinstance(item_index, int):
                raise ValueUnknownAtCompileTimeError(
                    "The displacement value of an expanded recv operation "
                    "must be known at compile time."
                )
            return QoalaReferenceInsideArray(self, item_index)
        else:
            return super().__getitem__(item_index)

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
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
        if QoalaProgram.compile_singular_comm_ops():
            for i in range(self.length):
                if self.base_type == int:
                    self.ir_value = qnet.recv_int(
                        remote=remote_name,
                        loc=source_location,
                    )
                elif self.base_type == float:
                    self.ir_value = qnet.recv_float(
                        remote=remote_name,
                        loc=source_location,
                    )
                else:
                    raise UnknownTypeError(
                        f"Cannot create recv operation for base type '{self.base_type}'"
                    )
        else:
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
                # This is generic enough to support mixed arrays and other values, but it's the best we can do so far.
                # Despite this waste, it can easily be fixed in the opt tool, by applying folding of constants.
                for array_val in val.members:
                    self.values.append(array_val)
                continue
            elif isinstance(val, QubitMeasure):
                # Measure yields an i1 value, we need to extend it to an i32 before we can send it
                cast_op = BitToInt(val)
                if qoala_type is QoalaInteger:
                    # Nothing extra to add in this case
                    final_casted_val = cast_op
                elif qoala_type is QoalaFloat:
                    # At this point, "cast_op" is an i32, and we are sending a float, so we
                    # still need to insert an extra cast
                    float_cast = IntToFloat(cast_op)
                    # And in this case, the final casted value is the f32 value
                    final_casted_val = float_cast
                else:
                    raise UnknownTypeError(
                        f"Send operation: target qoala type '{qoala_type.__name__}' cannot be "
                        f"sent with operation '{self.__class__.__name__}'"
                    )
                # Then we need to add the casted value, not the original one
                val_to_add = final_casted_val
            elif isinstance(val, base_type):
                val_to_add = QoalaNumericValue.from_immediate(val, self.debug_info)
            elif val.can_evaluate_to(qoala_type):
                val_to_add = val
            else:
                raise UnknownTypeError(
                    f"Send operation: value '{val}' cannot be converted to '{self.base_type}'"
                )
            self.values.append(val_to_add)
        QoalaProgram.add_to_current_function_body(self)

    def can_evaluate_to(self, cls) -> bool:
        return False

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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

        if isinstance(self.remote, DeclaredRemote):
            remote_name = self.remote.remote_name
        else:
            remote_name = self.remote
        if QoalaProgram.compile_singular_comm_ops():
            for element in elements:
                if self.base_type == int:
                    self.ir_value = qnet.send_int(
                        cin=element, remote=remote_name, loc=source_location
                    )
                elif self.base_type == float:
                    self.ir_value = qnet.send_float(
                        cin=element, remote=remote_name, loc=source_location
                    )
                else:
                    raise UnknownTypeError(
                        f"Cannot create send operation for base type '{self.base_type}'"
                    )
        else:
            tensor_shape = tensor.RankedTensorType.get(
                shape=[len(elements)], element_type=hir_base_type, loc=source_location
            )
            tensor_values = tensor.from_elements(
                elements=elements, result=tensor_shape, loc=source_location
            )
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
