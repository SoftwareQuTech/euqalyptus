# Quantum types

`euqalyptus.types.quantum` exposes three qubit-flavored classes plus a small factory function. All inherit from `Qubit` (which is the shared base that defines the gate methods).

Source: `euqalyptus/types/quantum/qubit.py`.

## `LocalQubit`

Represents a qubit allocated locally in the current node. Constructing a `LocalQubit()` inside a Qoala program records the equivalent of `qnet.new_qubit`.

```python
from euqalyptus.types.quantum import LocalQubit

q = LocalQubit()
q.X()                    # records qnet.x %q
q.H()                    # records qnet.hadamard
m = q.measure()          # records qnet.measure, returns a Bit AST
```

See [Qubit operations](qubit-ops.md) for the full method list.

## `EntangledQubit`

Represents a qubit that has been entangled with a remote node. You typically don't instantiate this directly — use the `Entangle()` factory below.

`EntangledQubit` carries the same gate methods as `LocalQubit`. The lowering treats them slightly differently: an `EntangledQubit` corresponds to a `qnet.eprs`-produced value rather than a `qnet.new_qubit` result.

## `Entangle("Name", n=1)` — the factory

```python
from euqalyptus.types.quantum import Entangle
from euqalyptus.operations import Remote

Remote("Bob")
q = Entangle("Bob")           # one entangled qubit shared with Bob
qs = Entangle("Bob", n=3)     # tuple of three entangled qubits
```

`Entangle` raises `UnknownRemoteError` if the named remote has not been declared with `Remote(...)` first.

When `n == 1`, returns a single `EntangledQubit`. When `n > 1`, returns a tuple of `EntangledQubit`s. Only the first element triggers the remote declaration in the AST.

## `ScopedQubit`

`ScopedQubit` is a thin wrapper used in branching constructs to express that a qubit is being conditionally manipulated and "yielded" back out of the conditional region. It accepts a `Qubit`, an `EntangledQubit`, or a tuple of `EntangledQubit`s.

```python
from euqalyptus.types.quantum import ScopedQubit

cond_q = ScopedQubit(qubit)
```

You typically reach for `ScopedQubit` only inside branching blocks. Branching is currently out of scope for this documentation; see `tests/bindings/test_branching.py` for examples.

## Where `qnet.qubit` comes from

In the emitted HIR, every qubit-typed value is `!qnet.qubit`. The mapping:

| SDK class | Recorded HIR op |
| --- | --- |
| `LocalQubit()` | `%q = qnet.new_qubit : !qnet.qubit` |
| `Entangle("Bob")` | `%q = qnet.eprs { remote = @Bob } : !qnet.qubit` |
| `Entangle("Bob", n=3)` | three `qnet.eprs` ops sharing the same remote |

After [the HIR→MIR lowering in qoala-mlir](<QOALA_MLIR_DOCS_URL>/passes/hir-to-mir/), each `!qnet.qubit` value is rewritten to an `i32` qubit pointer. From the user's perspective, that's invisible.

## API reference

::: euqalyptus.types.quantum.qubit
    options:
      members:
        - LocalQubit
        - EntangledQubit
        - Entangle
        - ScopedQubit
