# Teleportation — sender

This is the program that runs on the node holding the qubit to be teleported (here called **Alice**). It is taken verbatim from `qoala-compiler/teleportation/alice.py`.

## The program

```python
from euqalyptus import QoalaProgram
from euqalyptus.operations import Remote
from euqalyptus.types.quantum import Entangle, LocalQubit
from euqalyptus.operations.communication import send_int, recv_int

@QoalaProgram
def teleport():
    bob = Remote("Bob")

    # The local qubit holds the state we want to teleport.
    q_local = LocalQubit()

    # An EPR pair shared with Bob.
    q_ent = Entangle("Bob")

    # Bell-state measurement: CNOT then Hadamard, then measure both.
    q_local.cnot(q_ent)
    q_local.H()
    m_local = q_local.measure()
    m_ent   = q_ent.measure()

    # Send the two classical correction bits to Bob.
    send_int(bob, m_local)
    send_int(bob, m_ent)

    # Teleportation is one-shot here; we wait for an ack so the program
    # does not exit before Bob is done.
    result = recv_int(bob)


if __name__ == "__main__":
    _, hir = teleport.compile(singular_comm_ops=True)
    print(str(hir))
```

## Walkthrough

### Declare the remote

```python
bob = Remote("Bob")
```

Records a `qnet.remote @Bob` symbol at module scope. Without this, the `Entangle("Bob")` call below would raise `UnknownRemoteError`. See [Remotes](../../sdk/remotes.md).

### Allocate a local qubit and entangle with Bob

```python
q_local = LocalQubit()
q_ent   = Entangle("Bob")
```

`LocalQubit()` records `qnet.new_qubit`, producing a fresh `!qnet.qubit` SSA value. `Entangle("Bob")` records `qnet.eprs { remote = @Bob }`. After these two calls, the function body has two qubit values to operate on.

### Bell-state measurement

```python
q_local.cnot(q_ent)
q_local.H()
m_local = q_local.measure()
m_ent   = q_ent.measure()
```

The standard Bell-state measurement: `CNOT(q_local, q_ent)`, `H(q_local)`, then measure both. Both measurements emit `qnet.measure` and return `Bit`-typed AST nodes (`m_local` and `m_ent`).

Each `measure()` call **consumes** the corresponding qubit value. After this, you must not call any more methods on `q_local` or `q_ent` — the linearity verifier (`qnet-check-linear`) would reject it.

### Send correction bits

```python
send_int(bob, m_local)
send_int(bob, m_ent)
```

Each `send_int` records a `qnet.send_int` op with `m_local` (resp. `m_ent`) as its data and `@Bob` as its remote. Because we compile with `singular_comm_ops=True`, the SDK emits single-value `qnet.send_int` directly (rather than packing both into a tensor and sending with `qnet.send_ints`). See [Communication](../../sdk/communication.md).

### Wait for an ack

```python
result = recv_int(bob)
```

Records a `qnet.recv_int` op that blocks until Bob sends back a single classical value. In this example, the value isn't actually used — it just keeps Alice alive long enough for Bob to finish before her process exits.

## Compile

```python
_, hir = teleport.compile(singular_comm_ops=True)
print(str(hir))
```

`compile()` returns `(return_value, QoalaModule)`. The decorated function returns `None`, so the first element is `None`. The second is the compiled module — `str(...)` over it gives the textual HIR.

`singular_comm_ops=True` forces single-value classical ops in HIR. With the default (`False`), the same program would emit `qnet.send_ints` / `qnet.recv_ints` on tensor-typed values, which would then be unfolded at MIR level by `unfold-comm-ops`.

## What HIR looks like

The emitted HIR (abbreviated, pretty-printed) looks roughly like:

```mlir
module {
  qnet.remote @Bob

  qnet.func @teleport() {
    %q_local = qnet.new_qubit : !qnet.qubit
    %q_ent   = qnet.eprs { remote = @Bob } : !qnet.qubit

    %q_local2, %q_ent2 = qnet.cnot %q_local, %q_ent : !qnet.qubit, !qnet.qubit
    %q_local3 = qnet.hadamard %q_local2 : !qnet.qubit

    %m_local = qnet.measure %q_local3 : i1
    %m_ent   = qnet.measure %q_ent2 : i1

    qnet.send_int %m_local, @Bob : i32
    qnet.send_int %m_ent, @Bob : i32

    %ack = qnet.recv_int { remote = @Bob } : i32

    qnet.return
  }
}
```

(SSA names will differ — that's just the shape.)

## Take it through the rest of the pipeline

See [Continuing the pipeline](../../continuing-pipeline.md). For this program, the recommended invocation is:

```sh
qoala-opt alice.hir.mlir \
  --qnet-peephole-optimizations \
  --qnet-dead-code-elimination \
  --lower-qoala-hir-to-mir \
  --lower-qoala-mir-to-lir \
| qoala-translate --mlir-to-iqoala > alice.iqoala
```
