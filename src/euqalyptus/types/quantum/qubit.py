from abc import ABC
from typing import Tuple, Any

from typing_extensions import Self

from euqalyptus import QoalaProgram
from euqalyptus.ast.model import QoalaRuntimeQubit
from euqalyptus.ast.qubit import QoalaLocalQubit, QoalaEprs
from euqalyptus.errors import UnknownRemoteError
from euqalyptus.types.classical.floats import QoalaFloatingPointType
from euqalyptus.types.classical.integer import QoalaIntegerType
from euqalyptus.types.quantum import QoalaQuantumType


class Qubit(QoalaQuantumType, ABC):
    """Base class for every qubit type exposed by the SDK.

    A ``Qubit`` instance represents the quantum state stored in a
    physical qubit somewhere on the local quantum node. Constructing
    a concrete subclass — :class:`LocalQubit` for a locally-initialized
    qubit, :class:`EntangledQubit` for the local half of an EPR pair,
    or :class:`ScopedQubit` for a qubit that has to survive a branching
    region — records the allocation and initialization of that qubit
    in QoalaHIR. Gates, rotations, and measurement are performed by
    calling the corresponding methods on the qubit value.

    Operations follow HIR's value-based semantics: each method records
    a new SSA value for the qubit and conceptually "replaces" the
    current one. The wrapper objects on the Python side hide this so
    you can keep writing ``q.X(); q.measure()`` as if ``q`` were
    mutable.
    """

    def measure(self) -> QoalaIntegerType:  # type: ignore[empty-body]
        """Measure the qubit in the standard basis.

        Records a ``qnet.measure`` op on this qubit. The qubit value
        is consumed by the call; calling any other method on the same
        qubit afterwards will be rejected by the ``qnet-check-linear``
        verifier.

        Returns:
            A :class:`Bit`-typed SSA value carrying the measurement
            outcome (``0`` or ``1``).
        """
        pass

    def X(self):
        """Record an X (Pauli-X) gate on this qubit."""
        pass

    def Y(self):
        """Record a Y (Pauli-Y) gate on this qubit."""
        pass

    def Z(self):
        """Record a Z (Pauli-Z) gate on this qubit."""
        pass

    def T(self):
        """Record a T gate (Z-rotation of angle π/4) on this qubit."""
        pass

    def H(self):
        """Record a Hadamard gate on this qubit."""
        pass

    def K(self):
        """*Not implemented.* Placeholder for a K gate.

        Conceptually, a K gate would move the ``|0>`` state to ``+|i>``
        (positive Y) and vice versa. In the current SDK implementation
        this method is a no-op stub — calling it has no effect and the
        gate is *not* recorded in HIR. Use the rotations or
        ``H``/``S`` combinations instead.
        """
        pass

    def S(self):
        """Record an S gate (Z-rotation of angle π/2) on this qubit."""
        pass

    def rot_X(
        self,
        n: int | QoalaIntegerType = 0,
        d: int | QoalaIntegerType = 0,
        angle: float | QoalaFloatingPointType | None = None,
    ):
        """Record a rotation around the X axis.

        The rotation angle can be given in two ways. With the integer
        pair ``(n, d)`` it is interpreted as ``n · π / 2^d`` radians;
        for example, ``(n, d) = (1, 2)`` is a π/4 rotation. With the
        ``angle`` keyword, an arbitrary floating-point angle is taken
        directly and discretized later in the pipeline. If ``angle``
        is given, ``n`` and ``d`` are ignored.

        Args:
            n: Numerator of the discrete angle specification. Defaults
                to ``0``. May be a Python ``int`` or a Qoala
                integer-typed value.
            d: Denominator-exponent of the discrete angle
                specification. Defaults to ``0``. May be a Python
                ``int`` or a Qoala integer-typed value.
            angle: Optional explicit floating-point angle, in radians.
                Defaults to ``None``. When provided, takes precedence
                over ``n`` and ``d``.
        """
        pass

    def rot_Y(
        self,
        n: int | QoalaIntegerType = 0,
        d: int | QoalaIntegerType = 0,
        angle: float | QoalaFloatingPointType | None = None,
    ):
        """Record a rotation around the Y axis.

        Identical to :meth:`rot_X` but on the Y axis. See that method
        for the meaning of ``n``, ``d``, and ``angle``.

        Args:
            n: Numerator of the discrete angle specification.
            d: Denominator-exponent of the discrete angle
                specification.
            angle: Optional explicit floating-point angle, in radians.
        """
        pass

    def rot_Z(
        self,
        n: int | QoalaIntegerType = 0,
        d: int | QoalaIntegerType = 0,
        angle: float | QoalaFloatingPointType | None = None,
    ):
        """Record a rotation around the Z axis.

        Identical to :meth:`rot_X` but on the Z axis. See that method
        for the meaning of ``n``, ``d``, and ``angle``.

        Args:
            n: Numerator of the discrete angle specification.
            d: Denominator-exponent of the discrete angle
                specification.
            angle: Optional explicit floating-point angle, in radians.
        """
        pass

    def cnot(self, target: Self) -> None:
        """Record a CNOT gate with this qubit as control and ``target`` as target.

        Args:
            target: The target qubit. Must reside on the same node as
                this qubit (calling ``cnot`` between two qubits from
                different remotes is not meaningful in this SDK).
        """
        pass

    def cphase(self, target: Self) -> None:
        """Record a controlled-Z (CPHASE) gate.

        Args:
            target: The target qubit. Must reside on the same node as
                this qubit.
        """
        pass

    def cz(self, target: Self) -> None:
        """Synonym for :meth:`cphase`. Records a controlled-Z gate.

        Args:
            target: The target qubit. Must reside on the same node as
                this qubit.
        """
        pass

    def free(self) -> None:
        """*Not implemented.* Placeholder for releasing the qubit.

        Conceptually, freeing a qubit would return its virtual ID to
        the runtime's pool so the underlying physical qubit can be
        used to store another state. In the current SDK
        implementation this method is a no-op stub — calling it has
        no effect, and VirtID reuse is handled implicitly by the
        runtime after a measurement.
        """
        pass


class LocalQubit(Qubit):
    """A locally-allocated qubit.

    Constructing ``LocalQubit()`` inside a ``@QoalaProgram`` body
    records a ``qnet.new_qubit`` op, allocating and initializing a
    fresh local qubit on the current node. The returned value is a
    full :class:`Qubit` — all the gate, rotation, and measurement
    methods inherited from the base class are available on it.

    Returns:
        A :class:`Qubit` SSA value for the freshly allocated qubit.
    """

    def __new__(cls, *args, **kwargs):
        return QoalaLocalQubit()

    def __init__(self):
        # Nothing to do here
        pass


# Depending on the number of entangled qubits ("n" argument), this
# class behaves like
class EntangledQubit(Qubit):
    """The local half of an EPR pair shared with a remote node.

    Constructing ``EntangledQubit("Alice")`` inside a ``@QoalaProgram``
    body records a ``qnet.eprs { remote = @Alice }`` op, requesting an
    entangled pair with the named remote. The returned value is the
    local half of that pair, exposed as a regular :class:`Qubit`.

    Most users should prefer the :func:`Entangle` factory, which also
    handles the ``n > 1`` case of requesting several pairs in one go.

    Args:
        name: The symbolic name of the remote peer with which to
            entangle. The remote must have been declared via
            :class:`~euqalyptus.operations.Remote` earlier in the
            program.
    """

    def __new__(cls, name: str):
        return QoalaEprs(name)

    def __init__(self, name: str):
        # Nothing to do here
        pass


def Entangle(name: str, n: int = 1) -> EntangledQubit | Tuple[EntangledQubit, ...]:
    """Generate ``n`` entangled qubits with a remote peer.

    Records the appropriate number of ``qnet.eprs`` ops against the
    named remote and returns the local halves. With ``n = 1`` (the
    default), the function returns a single :class:`EntangledQubit`;
    with ``n > 1``, it returns a tuple of them.

    Args:
        name: The symbolic name of the remote peer. The remote must
            have been declared via
            :class:`~euqalyptus.operations.Remote` earlier in the
            program; passing an unknown name raises
            :class:`UnknownRemoteError`.
        n: The number of entangled pairs to request. Defaults to ``1``.

    Returns:
        A single :class:`EntangledQubit` if ``n == 1``, otherwise a
        tuple of ``n`` :class:`EntangledQubit` values, each
        representing the local half of one of the requested pairs.

    Raises:
        UnknownRemoteError: If ``name`` was not previously declared
            with :class:`~euqalyptus.operations.Remote`.
    """
    if QoalaProgram.get_declared_remote(name) is None:
        raise UnknownRemoteError(name)
    if n == 1:
        return EntangledQubit(name)
    else:
        # We return a tuple of EntangledQubits, declaring the remote ONLY for the first
        return tuple(EntangledQubit(name) for i in range(0, n))


# We inherit from Qubit, so this class behaves as a qubit. In this way,
# the IDE does not complain about "unknown methods" (like X(), measure(), etc.)
class ScopedQubit(Qubit):
    """A recording-time proxy for a qubit that must survive a branching region.

    ``ScopedQubit`` is used inside ``with if_cond(...)`` blocks to
    wrap a qubit whose post-branch identity must be the
    ``scf.if``-yielded SSA result rather than an in-region SSA value.
    Calling ``ScopedQubit(q)`` captures ``q`` and exposes the same
    qubit-method surface (``X``, ``Y``, ``measure``, …) on the
    wrapper; while the branch is open, calls on the wrapper are
    routed to the captured original, and the chain of operations
    applied through the wrapper is tracked so the front-end can emit
    a well-formed ``scf.yield``. After the branch exits, the wrapper
    rebinds to the SCF result and subsequent operations are recorded
    on that.

    See the implementation section of the accompanying paper for the
    full rationale; the test fixtures in
    ``tests/bindings/test_branching.py`` exercise the mechanism.

    Args:
        qubit: The qubit value to capture. Must already be a
            :class:`Qubit` (typically a :class:`LocalQubit` or
            :class:`EntangledQubit`) recorded earlier in the program.

    Raises:
        RuntimeError: If called without a qubit argument.
    """

    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            kwargs["qubit"] = args[0]
            return QoalaRuntimeQubit(**kwargs)
        else:
            raise RuntimeError("Missing qubit variable when creating ScopedQubit")

    def __init__(self, qubit: Qubit | EntangledQubit | Tuple[EntangledQubit, ...]):
        # Nothing to do here
        pass

    def assign(self, value: Any):
        """Re-assign the captured value of this scoped qubit.

        Used internally by the branching machinery to rebind a
        :class:`ScopedQubit` after a branch arm has been recorded; not
        typically called by user code.

        Args:
            value: The new captured value.
        """
        # Nothing to do here
        pass
