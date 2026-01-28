from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar, Optional, Type, List, Union

import qnet.dialects.arith as arith
import qnet.dialects.tensor as tensor
from qnet.extras.types import i32, ui32, f32, index, bool as mlir_bool
from qnet.ir import Context, Location
from typing_extensions import Self

from qoala.ast import QoalaExpression, checkbaseir
from qoala.ast.operations import QoalaOperation, with_operators
from qoala.errors import UnknownTypeError, OperandMismatchError
from qoala.utils.debug_info import DebugInfo, get_debug_info

_T = TypeVar("_T")


class Signedness(Enum):
    UNKNOWN = 0
    SIGNED = auto()
    UNSIGNED = auto()


class QoalaValue(QoalaExpression, Generic[_T], ABC):
    """
    Class used to represent a value in the AST. Nodes of this type (i.e.
    subclasses) are usually the leaves of the AST.
    """

    pass


@dataclass(init=False)
class QoalaNumericValue(QoalaValue[_T], ABC):
    signedness: Signedness
    width: int
    value: _T

    @classmethod
    def from_immediate(
        cls,
        value: _T,
        dbg_info: DebugInfo,
        is_index: bool = False,
        append_to_current_block: bool = True,
    ) -> Union["QoalaInteger", "QoalaFloat", "QoalaBool"]:
        if is_index:
            # We can't make an index out of a bool or a float
            assert isinstance(value, int)
            return QoalaInteger(
                value=value,
                width=32,
                signedness=Signedness.SIGNED,
                is_index_type=True,
                debug_info=dbg_info,
            )
        # Weird stuff... In python, "True" and "False" are both "bool" and "int" types, so
        # isinstance(True, bool) == True, and *also* isinstance(True, int) == True
        # This is very C-ish, and kinda unexpected... In any case, to avoid casting bool
        # immediates into QoalaIntegers (instead of QoalaBools), we first ask for bool
        # type, then integer. This takes advantage that isinstance(1, bool) == False
        elif isinstance(value, bool):
            return QoalaBool(
                value=value,
                debug_info=dbg_info,
                append_to_current_block=append_to_current_block,
            )
        elif isinstance(value, int):
            return QoalaInteger(
                value=value,
                width=32,
                signedness=Signedness.SIGNED,
                debug_info=dbg_info,
                append_to_current_block=append_to_current_block,
            )
        elif isinstance(value, float):
            return QoalaFloat(
                value=value,
                width=32,
                debug_info=dbg_info,
                append_to_current_block=append_to_current_block,
            )
        else:
            raise UnknownTypeError(
                f"A Qoala value could not be created from immediate '{value}'. "
                f"Supported immediate types are 'int' and 'float'."
            )


@with_operators(arith=True, bitwise=True, order=True)
class QoalaInteger(QoalaNumericValue[int]):
    def __init__(
        self,
        value: int,
        width: int,
        signedness: Signedness,
        debug_info: DebugInfo | None = None,
        is_index_type: bool = False,
        other: Optional[Self] = None,
        append_to_current_block: bool = True,
    ):
        super().__init__()
        if other is not None:
            self.width = other.width
            self.signedness = other.signedness
            if value is not None:
                self.value = value
            else:
                self.value = other.value
        else:
            self.width = width
            self.signedness = signedness
            self.value = value
        self.is_index_type = is_index_type
        if debug_info is not None:
            self.debug_info = debug_info
        else:
            self.debug_info = get_debug_info()
        if append_to_current_block:
            from qoala import QoalaProgram

            QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaInteger

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        if self.is_index_type:
            integer_type = index()
        elif self.signedness == Signedness.SIGNED:
            integer_type = i32()
        elif self.signedness == Signedness.UNSIGNED:
            integer_type = ui32()
        else:
            integer_type = i32()
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = arith.constant(
            value=self.value, result=integer_type, loc=source_location
        )


@with_operators(arith=True, bitwise=False, order=True)
class QoalaFloat(QoalaNumericValue[float]):

    def __init__(
        self,
        value: float,
        width: int,
        debug_info: DebugInfo | None = None,
        other: Optional[Self] = None,
        append_to_current_block: bool = True,
    ):
        super().__init__()
        if other is not None:
            self.width = other.width
            self.signedness = Signedness.UNKNOWN
            if value is not None:
                self.value = value
            else:
                self.value = other.value
        else:
            self.width = width
            self.signedness = Signedness.UNKNOWN
            self.value = value
        if debug_info is not None:
            self.debug_info = debug_info
        else:
            self.debug_info = get_debug_info()
        if append_to_current_block:
            from qoala import QoalaProgram

            QoalaProgram.current_function().append_to_current_block(self)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaFloat

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        float_type = f32()
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = arith.constant(
            value=self.value, result=float_type, loc=source_location
        )


@with_operators(arith=False, bitwise=True, order=False)
class QoalaBool(QoalaValue[bool]):
    def __init__(
        self,
        value: bool,
        debug_info: DebugInfo | None = None,
        other: Optional[Self] = None,
        append_to_current_block: bool = True,
    ):
        super().__init__()
        if other is not None:
            if value is not None:
                self.value = value
            else:
                self.value = other.value
        else:
            self.value = value
        if debug_info is not None:
            self.debug_info = debug_info
        else:
            self.debug_info = get_debug_info()
        if append_to_current_block:
            from qoala import QoalaProgram

            QoalaProgram.current_function().append_to_current_block(self)

    @classmethod
    def from_immediate(
        cls, value: bool, dbg_info: DebugInfo, append_to_current_block: bool = True
    ) -> "QoalaBool":
        return QoalaBool(
            value=value,
            debug_info=dbg_info,
            append_to_current_block=append_to_current_block,
        )

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        bool_type = mlir_bool()
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = arith.constant(
            value=self.value, result=bool_type, loc=source_location
        )

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaBool


# FIXME - In the meantime, we will model arrays as if they were
#         values. We might want to reconsider this decision in
#         the future.
_Qoala_Base_Type = TypeVar("_Qoala_Base_Type")
_Native_Base_Type = TypeVar("_Native_Base_Type")


@dataclass(init=False)
class QoalaArray(
    QoalaValue[QoalaExpression], Generic[_Qoala_Base_Type, _Native_Base_Type]
):
    qoala_type: Type
    base_type: Type
    base_size: int
    length: int
    members: List[QoalaExpression]

    def __init__(
        self,
        *elements,
        base_type: Type,
        base_size: int,
        length: int,
        base_clone: Optional[Self],
        append_to_current_block: bool = True,
    ):
        super().__init__()
        self.members = []
        self.base_type = base_type
        self.qoala_type = QoalaInteger if base_type == int else QoalaFloat
        self.base_size = base_size
        if base_clone is not None:
            for member in base_clone.members:
                self.members.append(member)
        if len(elements) > 0:
            self.length = 0
            for element in elements:
                assert isinstance(element, base_type) or isinstance(
                    element, QoalaExpression
                )
                if isinstance(element, QoalaExpression):
                    if not element.can_evaluate_to(self.qoala_type):
                        raise UnknownTypeError(
                            f"The element '{element}' cannot "
                            f"evaluate to type '{self.qoala_type}'"
                        )
                    else:
                        self.members.append(element)
                elif isinstance(element, base_type):
                    new_element: QoalaInteger | QoalaFloat
                    match self.base_type.__name__:
                        case "int":
                            new_element = QoalaInteger(
                                value=element, width=32, signedness=Signedness.SIGNED
                            )
                        case "float":
                            new_element = QoalaFloat(value=element, width=32)
                        case _:
                            raise UnknownTypeError(
                                f"Unknown base type '{self.base_type}'"
                            )
                    if new_element is not None:
                        self.members.append(new_element)
                else:
                    raise UnknownTypeError(
                        f"The element '{element}' cannot be "
                        f"inserted on an array of type '{self.base_type}'"
                    )
                self.length = self.length + 1
        else:
            self.length = length
        self.debug_info = get_debug_info()
        if append_to_current_block:
            from qoala import QoalaProgram

            QoalaProgram.current_function().append_to_current_block(self)

    def store(
        self, new_element: QoalaExpression | _Native_Base_Type
    ) -> QoalaExpression:
        to_add: QoalaExpression
        if isinstance(new_element, self.base_type):
            to_add = QoalaNumericValue.from_immediate(new_element, self.debug_info)
        else:
            assert isinstance(new_element, QoalaExpression)
            to_add = new_element
        from qoala.ast.operations.arrays import SetItem

        return QoalaOperation.create_expression_for_op(SetItem, self, to_add)

    def __len__(self) -> int:
        # TODO - Does this operation make sense?
        raise NotImplementedError("'len' operation for arrays not implemented")

    def __getitem__(self, item_index: QoalaExpression | int) -> QoalaExpression:
        from qoala.ast.operations.arrays import CastToIndex

        index_operand: QoalaInteger | QoalaFloat | QoalaBool | CastToIndex
        if isinstance(item_index, int):
            index_operand = QoalaNumericValue.from_immediate(
                item_index, self.debug_info, is_index=True
            )
        else:
            # The index is already a qoala expression, which can evaluate either to a float or int
            # If it evaluates to an int, we need to cast it to an integer
            if not item_index.can_evaluate_to(QoalaInteger):
                raise OperandMismatchError(
                    f"The index operand '{item_index}' cannot evaluate to an integer, "
                    f"hence it cannot be used index an array."
                )

            casted_index = QoalaOperation.create_expression_for_op(
                CastToIndex, item_index
            )
            index_operand = casted_index
        from qoala.ast.operations.arrays import GetItem

        return QoalaOperation.create_expression_for_op(GetItem, self, index_operand)

    def can_evaluate_to(self, cls) -> bool:
        return cls is QoalaArray

    def members_can_evaluate_to(self, cls) -> bool:
        return cls is self.qoala_type

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:  # type: ignore[override]
        ir_values = [element.ir_value for element in self.members]
        if self.base_type is int:
            hir_base_type = i32()
        elif self.base_type is float:
            hir_base_type = f32()
        else:
            raise UnknownTypeError(
                f"Base type '{self.base_type.__name__}' for arrays is not supported"
            )
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        result_type = tensor.RankedTensorType.get(
            shape=[self.length], element_type=hir_base_type, loc=source_location
        )
        self.ir_value = tensor.from_elements(
            elements=ir_values, result=result_type, loc=source_location
        )


@with_operators(arith=True, bitwise=False, order=False)
class QoalaReferenceInsideArray(QoalaExpression):
    """
    A simple reference to value inside a QoalaArray that will be resolved when generating the IR.
    Being this said, this object *should not yield any additional IR operation*, but rather be
    a "proxy" to the IR of another expression.
    The aforementioned behavior is useful when dealing with operations that are "expanded", and
    the IR value references is only known when generating the IR (*after* generating the AST).
    """

    def __init__(self, base_expression: QoalaArray, idx: int):
        super().__init__()
        self._base_expression = base_expression
        self._index = idx
        from qoala import QoalaProgram

        QoalaProgram.current_function().append_to_current_block(self)

    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        self.ir_value = self._base_expression.ir_values[self._index]

    def can_evaluate_to(self, cls) -> bool:
        return self._base_expression.qoala_type is cls


class QoalaBit(QoalaValue[int], ABC):
    """
    Represents the result of performing a measurement of the qubit.
    Theoretically, the result of measuring a qubit can be either 0 or 1.
    For this reason, this class is called "bit"
    IMPORTANT: Despite it is possible to use the `Bit` type from the
    qoala.types.classical.integer packages to get an object of this type,
    this usage is *not* recommended. This class has been conceived to
    model the _type returned by the 'measure' operation on a qubit_.
    """

    pass
