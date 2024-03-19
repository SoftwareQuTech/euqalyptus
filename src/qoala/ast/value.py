from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar, Self, Optional, Type, List

import qoalahir.dialects.arith as arith
import qoalahir.dialects.tensor as tensor
from qoalahir.extras.types import i32, ui32, f32, index
from qoalahir.ir import Context

from qoala import QoalaProgram
from qoala.ast import QoalaExpression, QoalaStatement
from qoala.ast.errors import UnknownTypeError, OperandMismatchError
from qoala.ast.operations import QoalaOperation, with_arith_operators

_T = TypeVar("_T")


class Signedness(Enum):
    UNKNOWN = 0
    SIGNED = auto()
    UNSIGNED = auto()


class QoalaValue(QoalaExpression, Generic[_T]):
    """
    Class used to represent a value in the AST. Nodes of this type (i.e.
    subclasses) are usually the leaves of the AST.
    """
    pass


@dataclass(init=False)
class QoalaNumericValue(QoalaValue[_T]):
    signedness: Signedness
    width: int
    value: _T

    @classmethod
    def from_immediate(cls, value: _T, is_index: bool = False) -> Self:
        if is_index:
            return QoalaInteger(value=value, width=32, signedness=Signedness.SIGNED, is_index_type=True)
        elif isinstance(value, int):
            return QoalaInteger(value=value, width=32, signedness=Signedness.SIGNED)
        elif isinstance(value, float):
            return QoalaFloat(value=value, width=32)
        else:
            raise UnknownTypeError(f"A Qoala value could not be created from immediate '{value}'. "
                                   f"Supported immediate types are 'int' and 'float'.")


@with_arith_operators
class QoalaInteger(QoalaNumericValue[int]):
    def __init__(
            self,
            value: _T,
            width: int,
            signedness: Signedness,
            is_index_type: bool = False,
            other: Optional[Self] = None
    ):
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
        QoalaProgram.add_to_body(self)

    def can_evaluate_to(self, cls):
        if cls == QoalaInteger:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        if self.is_index_type:
            integer_type = index()
        elif self.signedness == Signedness.SIGNED:
            integer_type = i32()
        elif self.signedness == Signedness.UNSIGNED:
            integer_type = ui32()
        else:
            integer_type = i32()
        self._qoala_hir_val = arith.constant(value=self.value, result=integer_type)
        return self._qoala_hir_val


@with_arith_operators
class QoalaFloat(QoalaNumericValue[float]):
    def __init__(
            self,
            value: _T,
            width: int,
            other: Optional[Self] = None
    ):
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
        QoalaProgram.add_to_body(self)

    def to_hir(self, ctx: Context):
        float_type = f32()
        self._qoala_hir_val = arith.constant(value=self.value, result=float_type)
        return self._qoala_hir_val

    def can_evaluate_to(self, cls):
        if cls == QoalaFloat:
            return True
        else:
            return False


QoalaFloatOrExpression = QoalaFloat | QoalaExpression
QoalaIntegerOrExpression = QoalaInteger | QoalaExpression

ImmediateQFloatOrExpression = QoalaFloatOrExpression | float
ImmediateQIntOrExpression = QoalaIntegerOrExpression | int


# FIXME - In the meantime, we will model arrays as if they were
#         values. We might want to reconsider this decision in
#         the future.
@dataclass(init=False)
class QoalaArray(QoalaValue[QoalaExpression], Generic[_T]):
    base_type: Type
    base_size: int
    length: int
    members: List[QoalaExpression]

    def __init__(
            self,
            *elements,
            base_type: Type,
            base_size: int,
            length: int
    ):
        self.members = []
        self.base_type = base_type
        self.base_size = base_size
        if len(elements) > 0:
            self.length = 0
            for element in elements:
                assert isinstance(element, base_type) or isinstance(element, QoalaExpression)
                if isinstance(element, QoalaExpression):
                    self.members.append(element)
                elif isinstance(element, base_type):
                    match self.base_type.__name__:
                        case "int":
                            new_element = QoalaInteger(value=element, width=32, signedness=Signedness.SIGNED)
                        case "float":
                            new_element = QoalaFloat(value=element, width=32)
                        case _:
                            raise UnknownTypeError(f"Unknown base type '{self.base_type}'")
                    if new_element is not None:
                        self.members.append(new_element)
                else:
                    raise UnknownTypeError(f"The element '{element}' cannot be "
                                           f"inserted on an array of type '{self.base_type}'")
                self.length = self.length + 1
        else:
            self.length = length
        QoalaProgram.add_to_body(self)

    def store(self, new_element: QoalaExpression | _T) -> QoalaStatement:
        if isinstance(new_element, self.base_type):
            to_add = QoalaNumericValue.from_immediate(new_element, is_index=True)
        else:
            to_add = new_element
        from qoala.ast.operations.arrays import SetItem
        return QoalaOperation._create_expression_for_op(SetItem, self, to_add)

    def __len__(self) -> int:
        # TODO - Does this operation make sense?
        raise NotImplementedError("'len' operation for arrays not implemented")

    def __getitem__(self, item_index: QoalaExpression | int) -> QoalaExpression:
        if isinstance(item_index, int):
            index_operand = QoalaNumericValue.from_immediate(item_index, is_index=True)
        else:
            # The index is already a qoala expression, which can evaluate either to a float or int
            # If it evaluates to an int, we need to cast it to an integer
            if not item_index.can_evaluate_to(QoalaInteger):
                raise OperandMismatchError(f"The index operand '{item_index}' cannot evaluate to an integer, "
                                           f"hence it cannot be used index an array.")
            from qoala.ast.operations.arrays import CastToIndex
            casted_index = QoalaOperation._create_expression_for_op(CastToIndex, item_index)
            index_operand = casted_index
        from qoala.ast.operations.arrays import GetItem
        return QoalaOperation._create_expression_for_op(GetItem, self, index_operand)

    def can_evaluate_to(self, cls):
        if cls == QoalaArray:
            return True
        else:
            return False

    def to_hir(self, ctx: Context):
        # TODO - Implement the HIR representation for arrays - tensor or vector?
        elements = [element._qoala_hir_val for element in self.members]
        if self.base_type is int:
            hir_base_type = i32()
        elif self.base_type is float:
            hir_base_type = f32()
        else:
            raise UnknownTypeError(f"Base type '{self.base_type.__name__}' for arrays is not supported")
        result_type = tensor.RankedTensorType.get([self.length], hir_base_type)
        self._qoala_hir_val = tensor.from_elements(elements=elements, result=result_type)
        return self._qoala_hir_val


class QoalaBit(QoalaValue[int]):
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
