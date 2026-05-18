from typing import List

from euqalyptus.ast.model import QoalaRuntimeValue
from euqalyptus.ast.operations import QoalaOperation
from euqalyptus.ast.operations.communication import (
    RecvIntsOp,
    RecvFloatsOp,
    RecvIntOp,
    RecvFloatOp,
    SendIntsOp,
    SendFloatsOp,
    DeclaredRemote,
)
from euqalyptus.ast.value import QoalaInteger, QoalaFloat, QoalaArray, QoalaBit
from euqalyptus.operations import Remote
from euqalyptus.types.classical import (
    IntArray,
    FloatArray,
    ScopedVar,
    NumericOperandsOverload,
    BitwiseOperandsOverload,
)
from euqalyptus.types.classical.floats import QoalaFloatingPointType
from euqalyptus.types.classical.integer import QoalaIntegerType


class RecvInts(IntArray):
    """Record a tensor-valued classical receive from a remote peer.

    Calling ``RecvInts(remote, length)`` inside a ``@QoalaProgram`` body
    records a ``qnet.recv_ints``-shaped AST node that, at execution time,
    blocks until the peer has sent ``length`` integer values. The result
    behaves like an :class:`~euqalyptus.types.classical.IntArray` and can
    be indexed and stored against.

    Args:
        remote_name: The remote peer to receive from. May be a
            :class:`~euqalyptus.operations.Remote` (or a
            :class:`DeclaredRemote`) returned by a previous
            ``Remote("Name")`` call, or just the peer's name as a
            ``str``.
        length: The number of integer values to receive.

    Returns:
        An :class:`~euqalyptus.types.classical.IntArray`-typed AST node
        carrying the received values.

    Raises:
        AssertionError: If ``remote_name`` is not a ``DeclaredRemote`` or
            ``str``.
    """

    def __new__(cls, remote_name: Remote | str, length: int):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvIntsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvInt(QoalaIntegerType, NumericOperandsOverload, BitwiseOperandsOverload):
    """Record a single-value classical integer receive from a remote peer.

    Calling ``RecvInt(remote)`` (or the alias ``recv_int(remote)``)
    inside a ``@QoalaProgram`` body records a ``qnet.recv_int``-shaped
    AST node that, at execution time, blocks until the peer has sent
    one integer value. Unlike the send side, the scalar receive is its
    own first-class class — the ``compile(singular_comm_ops=True)``
    flag does not need to be set to use it.

    Args:
        remote_name: The remote peer to receive from. May be a
            :class:`~euqalyptus.operations.Remote` (or a
            :class:`DeclaredRemote`) returned by a previous
            ``Remote("Name")`` call, or the peer's name as a ``str``.

    Returns:
        A :class:`QoalaIntegerType`-typed AST node carrying the received
        value. The returned value supports the usual numeric and
        bitwise operators.

    Raises:
        AssertionError: If ``remote_name`` is not a ``DeclaredRemote`` or
            ``str``.
    """

    def __new__(cls, remote_name: Remote | str):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvIntOp(remote_name=remote_name)

    def __init__(self, remote_name: Remote | str):
        # Nothing to do here
        pass


class RecvFloats(FloatArray, NumericOperandsOverload, BitwiseOperandsOverload):
    """Record a tensor-valued classical-float receive from a remote peer.

    Calling ``RecvFloats(remote, length)`` inside a ``@QoalaProgram``
    body records a ``qnet.recv_floats``-shaped AST node that, at
    execution time, blocks until the peer has sent ``length``
    floating-point values. The result behaves like a
    :class:`~euqalyptus.types.classical.FloatArray`.

    Args:
        remote_name: The remote peer to receive from. May be a
            :class:`~euqalyptus.operations.Remote` (or a
            :class:`DeclaredRemote`) returned by a previous
            ``Remote("Name")`` call, or the peer's name as a ``str``.
        length: The number of floating-point values to receive.

    Returns:
        A :class:`~euqalyptus.types.classical.FloatArray`-typed AST node
        carrying the received values.

    Raises:
        AssertionError: If ``remote_name`` is not a ``DeclaredRemote`` or
            ``str``.
    """

    def __new__(cls, remote_name: Remote | str, length: int):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvFloatsOp(remote_name=remote_name, length=length)

    def __init__(self, remote_name: Remote | str, length: int):
        # Nothing to do here
        super().__init__()


class RecvFloat(QoalaFloatingPointType):
    """Record a single-value classical-float receive from a remote peer.

    Calling ``RecvFloat(remote)`` (or the alias ``recv_float(remote)``)
    inside a ``@QoalaProgram`` body records a ``qnet.recv_float``-shaped
    AST node that, at execution time, blocks until the peer has sent
    one floating-point value.

    Args:
        remote_name: The remote peer to receive from. May be a
            :class:`~euqalyptus.operations.Remote` (or a
            :class:`DeclaredRemote`) returned by a previous
            ``Remote("Name")`` call, or the peer's name as a ``str``.

    Returns:
        A :class:`QoalaFloatingPointType`-typed AST node carrying the
        received value.

    Raises:
        AssertionError: If ``remote_name`` is not a ``DeclaredRemote`` or
            ``str``.
    """

    def __new__(cls, remote_name: Remote | str):
        assert isinstance(remote_name, (DeclaredRemote, str))
        return RecvFloatOp(remote_name=remote_name)

    def __init__(self, remote_name: Remote | str):
        pass


# TODO - Inherit from what?
class SendInts:
    """Record a (possibly variadic) classical-integer send to a remote peer.

    Calling ``SendInts(remote, v1, v2, ...)`` inside a ``@QoalaProgram``
    body records a ``qnet.send_ints`` AST node that, at execution time,
    sends the given integer values to ``remote`` as a single tensor
    payload. The scalar aliases ``send_int`` and ``send_ints`` both
    point at this class — the difference is whether
    ``compile(singular_comm_ops=True)`` is set: with the flag, a single
    value emits the scalar HIR op ``qnet.send_int``; without it (the
    default), a one-element tensor is emitted.

    Args:
        remote_name: The remote peer to send to. May be a
            :class:`~euqalyptus.operations.Remote` (or a
            :class:`DeclaredRemote`) returned by a previous
            ``Remote("Name")`` call, or the peer's name as a ``str``.
        *args: One or more values to send. Each value must be an
            :class:`IntArray`, a :class:`QoalaIntegerType`, a
            :class:`QoalaBit`, a runtime-typed
            :class:`QoalaRuntimeValue` / :class:`QoalaOperation` that
            evaluates to an integer or bit, or a Python ``int``
            literal. ``QoalaBit`` values are widened to integers
            automatically before sending.

    Returns:
        A :class:`SendIntsOp` AST node representing the send.

    Raises:
        AssertionError: If ``remote_name`` is not a ``DeclaredRemote``
            or ``str``, or if any positional argument is not of one of
            the supported types.
    """

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
    """Record a (possibly variadic) classical-float send to a remote peer.

    Calling ``SendFloats(remote, v1, v2, ...)`` inside a
    ``@QoalaProgram`` body records a ``qnet.send_floats`` AST node
    that, at execution time, sends the given values to ``remote`` as a
    single tensor payload. As with :class:`SendInts`, the scalar
    aliases ``send_float`` / ``send_floats`` both point at this class;
    ``compile(singular_comm_ops=True)`` selects whether a single value
    is emitted as the scalar HIR op ``qnet.send_float`` or as a
    one-element tensor.

    Args:
        remote_name: The remote peer to send to. May be a
            :class:`~euqalyptus.operations.Remote` (or a
            :class:`DeclaredRemote`) returned by a previous
            ``Remote("Name")`` call, or the peer's name as a ``str``.
        *args: One or more values to send. Each value must be a
            :class:`FloatArray`, a :class:`QoalaFloatingPointType`, a
            :class:`QoalaIntegerType`, a :class:`QoalaBit`, a runtime
            value that evaluates to one of those, or a Python ``float``
            literal. Integer- and bit-typed values are widened to
            floats automatically before sending.

    Returns:
        A :class:`SendFloatsOp` AST node representing the send.

    Raises:
        AssertionError: If ``remote_name`` is not a ``DeclaredRemote``
            or ``str``, or if any positional argument is not of one of
            the supported types.
    """

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
"""Lowercase alias of :class:`RecvInt`. Records ``qnet.recv_int``."""

recv_ints = RecvInts
"""Lowercase alias of :class:`RecvInts`. Records ``qnet.recv_ints``."""

recv_float = RecvFloat
"""Lowercase alias of :class:`RecvFloat`. Records ``qnet.recv_float``."""

recv_floats = RecvFloats
"""Lowercase alias of :class:`RecvFloats`. Records ``qnet.recv_floats``."""

send_int = SendInts
"""Lowercase scalar alias of :class:`SendInts`. With
``compile(singular_comm_ops=True)``, the SDK emits ``qnet.send_int`` for
a single-value send; with the default ``compile()``, it emits
``qnet.send_ints`` on a one-element tensor."""

send_ints = SendInts
"""Lowercase alias of :class:`SendInts`. Records ``qnet.send_ints`` on a
tensor of values."""

send_float = SendFloats
"""Lowercase scalar alias of :class:`SendFloats`. With
``compile(singular_comm_ops=True)``, the SDK emits ``qnet.send_float``
for a single-value send; with the default ``compile()``, it emits
``qnet.send_floats`` on a one-element tensor."""

send_floats = SendFloats
"""Lowercase alias of :class:`SendFloats`. Records ``qnet.send_floats``
on a tensor of values."""
