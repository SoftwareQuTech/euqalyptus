# Communication

Classical communication between nodes is expressed as send/recv operations parameterized by a remote name. The SDK exposes both single-value and array forms.

Source: `euqalyptus/operations/communication.py`.

## Importing

```python
from euqalyptus.operations.communication import (
    send_int, recv_int,
    send_float, recv_float,
    send_ints, recv_ints,
    send_floats, recv_floats,
)
```

The corresponding class-style names (`SendInt`, `RecvInt`, `SendInts`, …) are also exported and behave identically — pick whichever style you prefer.

## Single-value ops

| Op | Signature | HIR op |
| --- | --- | --- |
| `send_int(remote, value)` | `(Remote\|str, IntArray\|QoalaIntegerType\|int) -> None` | `qnet.send_int` |
| `recv_int(remote)` | `(Remote\|str) -> Int` | `qnet.recv_int` |
| `send_float(remote, value)` | `(Remote\|str, FloatArray\|QoalaFloatingPointType\|float) -> None` | `qnet.send_float` |
| `recv_float(remote)` | `(Remote\|str) -> Float` | `qnet.recv_float` |

```python
bob = Remote("Bob")
m = q.measure()
send_int(bob, m)            # m is a Bit; auto-extended to i32
ack = recv_int(bob)
```

`send_int` accepts a `Bit` or a Python `int` literal, which is converted to a 32-bit value before being recorded.

## Array ops

| Op | Signature | HIR op |
| --- | --- | --- |
| `send_ints(remote, *values)` | variadic `IntArray\|Int\|int` arguments | `qnet.send_ints` |
| `recv_ints(remote, length)` | `(Remote\|str, int) -> IntArray` | `qnet.recv_ints` |
| `send_floats(remote, *values)` | variadic `FloatArray\|Float\|float` arguments | `qnet.send_floats` |
| `recv_floats(remote, length)` | `(Remote\|str, int) -> FloatArray` | `qnet.recv_floats` |

```python
xs = recv_ints("Alice", 4)        # IntArray of length 4
send_ints("Alice", xs[0], xs[1])  # cherry-pick and send back
```

The variadic send forms accept individual values, an `IntArray`/`FloatArray`, or any mixture — they are flattened during recording.

## Single vs. multi-value forms

The single-value forms (`send_int`, `recv_int`, …) and the array forms (`send_ints`, `recv_ints`, …) coexist for two reasons:

1. **Convenience.** Most user programs send/receive a small fixed number of classical values; single-value ops match that shape exactly.
2. **Tensor avoidance.** The multi-value ops use `tensor<?xi32>` and `tensor<?xf32>` types in HIR. Tensors are heavier to lower than `i32`/`f32` SSA values. If you `compile(singular_comm_ops=True)`, the SDK emits only single-value ops, sidestepping tensor lowering altogether.

If you compile with `singular_comm_ops=False` (the default), the array ops emit `qnet.send_ints` / `qnet.recv_ints` (etc.) in HIR. They are then **unfolded** into single-value ops at MIR level by [`unfold-comm-ops`](https://softwarequtech.github.io/qoala-mlir/passes/mir/) — unless you disable that pass via `--lower-qoala-mir-to-lir=disable-unfold-comm-ops=true`.

## Errors

| Exception | Raised when |
| --- | --- |
| `UnknownRemoteError` | The named remote was not previously declared with `Remote(...)`. |
| `InvalidArrayArgumentError` | A `send_ints` / `send_floats` argument is the wrong type for the array. |
| `OperandMismatchError` | An overload's argument count or type doesn't match. |

Recv operations don't take values, so they cannot raise type-mismatch errors at SDK level.

## What ends up in HIR

A simple round-trip:

```python
@QoalaProgram
def example():
    alice = Remote("Alice")
    q = Entangle("Alice")
    m = q.measure()
    send_int(alice, m)
    ack = recv_int(alice)
```

becomes:

```mlir
module {
  qnet.remote @Alice
  %ent = qnet.eprs { remote = @Alice } : !qnet.qubit
  %m = qnet.measure %ent : i1
  qnet.send_int %m, @Alice : i32
  %ack = qnet.recv_int { remote = @Alice } : i32
}
```

## API reference

::: euqalyptus.operations.communication
    options:
      members:
        - RecvInt
        - RecvInts
        - RecvFloat
        - RecvFloats
        - SendInts
        - SendFloats
        - recv_int
        - recv_ints
        - recv_float
        - recv_floats
        - send_int
        - send_ints
        - send_float
        - send_floats
