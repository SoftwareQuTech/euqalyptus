# Remotes

Remote nodes are referenced by name. Before any classical or entanglement op can target a remote, the program must declare its name with `Remote(...)`.

Source: `euqalyptus/operations/__init__.py`.

![Entanglement flow](../assets/figures/entanglement-flow.svg)

## `Remote("Name")`

```python
from euqalyptus.operations import Remote

bob = Remote("Bob")
```

`Remote(name)` records a `DeclaredRemote` in the active program's module. The first time a given name appears, a `qnet.remote` symbol is emitted at module scope. Subsequent calls with the same name return the same `DeclaredRemote` object — i.e. it's idempotent within a `compile()`.

You typically do this once at the top of your program for each remote node it talks to:

```python
@QoalaProgram
def alice_to_bob():
    Remote("Bob")
    Remote("Charlie")          # talks to two remote nodes
    ...
```

## Using a declared remote

Communication and entanglement operations accept either a `Remote(...)` value or a plain string:

```python
bob = Remote("Bob")
q1 = Entangle("Bob")           # via name
q2 = Entangle(bob)             # via the Remote object — equivalent
send_int(bob, m)               # via the Remote object
send_int("Bob", m)             # via name — equivalent
```

The two forms are interchangeable; both end up referencing the same module-scope `qnet.remote @Bob` symbol after lowering.

## What gets emitted

For each unique name passed to `Remote(...)` during a single `compile()`, the resulting HIR includes:

```mlir
qnet.remote @Bob
```

at module scope. After [the MIR→LIR lowering in qoala-mlir](https://softwarequtech.github.io/qoala-mlir/passes/mir-to-lir/), this becomes:

```mlir
qremote.remote @Bob
```

Every send/recv/eprs op references the symbol via a `FlatSymbolRefAttr` named `remote`, and a verifier rejects any reference that does not resolve to a valid `qremote.remote` declaration.

## Limits

- A given remote name may not be redeclared with a different `DeclaredRemote` within the same program — the SDK enforces this in `QoalaProgram.add_declared_remote`.
- The SDK does not check that the name corresponds to an actually reachable peer in the runtime; that's the runtime's job. From euqalyptus's perspective, the name is just a symbol.

## API reference

::: euqalyptus.operations.Remote
