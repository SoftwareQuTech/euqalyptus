import math
from abc import ABC
from dataclasses import dataclass
from typing import Type, Optional

import qnet.dialects.qnet as qnet
from qnet.ir import Context, Location

from qoala import QoalaProgram
from qoala.ast import checkbaseir, QoalaExpression
from qoala.ast.operations import QoalaOperation
from qoala.ast.qubit import QoalaQubit
from qoala.ast.value import (
    QoalaFloatOrExpression,
    QoalaNumericValue,
    QoalaBit,
)
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
        QoalaProgram.current_function().append_to_current_block(self)

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
        QoalaProgram.current_function().append_to_current_block(self)


class RotateX(Rotate):

    def __init__(self, qubit: QoalaExpression, angle: QoalaFloatOrExpression):
        super().__init__(qubit=qubit, angle=angle)

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
            def compile(
                self, ctx: Context, location: Optional[Location] = None
            ) -> None:
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
        QoalaProgram.current_function().append_to_current_block(self)

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        source_location = Location.file(
            filename=self.debug_info.filename,
            line=self.debug_info.line_start,
            col=self.debug_info.col_start,
            context=ctx,
        )
        self.ir_value = qnet.hadamard(self.qubit.ir_value, loc=source_location)
        # We then register that the qubit has a "new" value
        self.qubit.ir_value = self.ir_value


@dataclass(init=False)
class CNotGate(_QubitBaseOperation):
    target: QoalaQubit

    def __init__(self, qubit: QoalaExpression, target: QoalaExpression):
        super().__init__(qubit=qubit)
        assert target.can_evaluate_to(QoalaQubit)
        self.target = target
        QoalaProgram.current_function().append_to_current_block(self)

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
        QoalaProgram.current_function().append_to_current_block(self)

    @checkbaseir
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
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
