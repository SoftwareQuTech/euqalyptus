# Qubit operations

Every method documented here is defined on the `Qubit` base class and inherited by `LocalQubit`, `EntangledQubit`, and `ScopedQubit`. Calling a method records the corresponding HIR op into the active program's body.

Source: `euqalyptus/types/quantum/qubit.py`.

## Single-qubit Pauli and Clifford gates

| Method | HIR op | Notes |
| --- | --- | --- |
| `q.X()` | `qnet.x` | Pauli X (Hermitian). |
| `q.Y()` | `qnet.y` | Pauli Y (Hermitian). |
| `q.Z()` | `qnet.z` | Pauli Z (Hermitian). |
| `q.H()` | `qnet.hadamard` | Hadamard (Hermitian). |
| `q.T()` | rotation form | π/4 around Z. Lowered through the angle-discretization machinery. |
| `q.S()` | rotation form | π/2 around Z. |
| `q.K()` | rotation form | Maps `|0⟩` to `+|i⟩` (positive Y) and vice versa. |

```python
q = LocalQubit()
q.H()
q.X()
```

## Single-qubit rotations

`rot_X`, `rot_Y`, and `rot_Z` accept either an integer-pair `(n, d)` encoding `angle = n·π / 2^d`, or an explicit floating-point `angle=`:

```python
q.rot_X(n=1, d=2)                # π/4 rotation around X
q.rot_Y(angle=0.7853981633974483)  # explicit float angle
```

Signature for all three:

```python
def rot_X(
    self,
    n: int | QoalaIntegerType = 0,
    d: int | QoalaIntegerType = 0,
    angle: float | QoalaFloatingPointType | None = None,
) -> None:
    ...
```

If `angle` is provided, `n` and `d` are ignored and the SDK records a `qnet.rot_*` (float-angle) op. The angle is later discretized — at MIR level, `lower-float-rotations` rewrites it to `qmem.rot_*_int` form using the runtime helper if needed. See [qoala-mlir / Passes / MIR helpers](https://softwarequtech.github.io/qoala-mlir/passes/mir/).

If `angle` is `None`, the SDK records `qnet.rot_*_int` directly with `n` and `d`.

## Two-qubit gates

Methods that take a target qubit:

| Method | HIR op | Notes |
| --- | --- | --- |
| `q.cnot(target)` | `qnet.cnot` | CNOT controlled by `q`, target `target`. |
| `q.cphase(target)` | `qnet.cz` | CPHASE / CZ. The two are aliases on the SDK side. |
| `q.cz(target)` | `qnet.cz` | Synonym for `cphase`. |

```python
ctrl = LocalQubit()
tgt  = LocalQubit()
ctrl.cnot(tgt)
```

`crot_X` (controlled X-rotation) is **not** exposed as a method on `Qubit`. It exists as an op in the dialect but is reachable only through the lowering passes (it appears in MIR/LIR after MIR-level rewrites). If you need a controlled rotation in user code, decompose it manually.

## Measurement

```python
m = q.measure()
```

`measure` is the standard-basis measurement. It records `qnet.measure` and returns a `QoalaIntegerType` AST node (effectively a `Bit`). After this point, the qubit value has been *consumed* in HIR — using `q` again is a linearity violation and will fail `qnet-check-linear` downstream. Reuse the *returned* AST value (the measurement outcome) instead.

## Free

```python
q.free()
```

Marks the qubit as released so its physical slot can be reused. There is no corresponding `qnet.*` op at HIR level — `free()` is consumed by the AST builder and surfaces during the MIR lifecycle work. In practice you can ignore it for most short programs; it becomes relevant when you write programs with many qubits and want to control reuse.

## Linearity invariant

Each qubit value should be consumed at most once. The SDK doesn't enforce this at the Python level (a method call doesn't visibly "consume" `self`), but [qoala-mlir's `qnet-check-linear`](https://softwarequtech.github.io/qoala-mlir/passes/hir/) does. If you observe a `Use of qubit after consumed` error from `qoala-opt`, it usually means the program reused a qubit value after `measure()` or after a gate operation that, in HIR, returns a *new* qubit value.

In SDK terms, the rules of thumb:

- After `q.measure()`, do not call any further methods on `q`.
- For operations that take a target (`q.cnot(target)`), the recorded op produces fresh qubit values for both — your `q` and `target` Python references are kept synced internally, so you don't have to re-bind them.

## API reference

The qubit-operation methods are defined on the abstract `Qubit` base class; every concrete qubit type ([LocalQubit](types-quantum.md#api-reference), [EntangledQubit](types-quantum.md#api-reference), [ScopedQubit](types-quantum.md#api-reference)) inherits them.

::: euqalyptus.types.quantum.qubit.Qubit
    options:
      members:
        - measure
        - X
        - Y
        - Z
        - H
        - S
        - T
        - K
        - rot_X
        - rot_Y
        - rot_Z
        - cnot
        - cphase
        - cz
        - free
