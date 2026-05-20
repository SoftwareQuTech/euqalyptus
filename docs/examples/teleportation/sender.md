# Teleportation — sender

This is the program that runs on the node holding the qubit to be teleported — here called **Alice**. It is taken verbatim from `qoala-compiler/examples/teleportation/alice.py`.

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

The first call records the remote: `bob = Remote("Bob")` registers a `qnet.remote @Bob` symbol at module scope. Without this declaration, the `Entangle("Bob")` call below would raise `UnknownRemoteError`. See [Remotes](../../sdk/remotes.md) for the full surface.

The program then allocates the two qubits it needs. `LocalQubit()` records `qnet.new_qubit` and yields a fresh `!qnet.qubit` SSA value, while `Entangle("Bob")` records `qnet.eprs { remote = @Bob }` and yields the local half of a Bell pair shared with Bob. After these two calls, the function body has two qubit values to operate on.

The body of the program is the standard Bell-state measurement: `CNOT(q_local, q_ent)` then `H(q_local)`, followed by a measurement on each qubit. Both measurements emit `qnet.measure` and return `Bit`-typed AST nodes (here named `m_local` and `m_ent`). Each `measure()` call *consumes* the corresponding qubit value — calling another method on `q_local` or `q_ent` after the measurement would be rejected by the linearity verifier (`qnet-check-linear`).

The two correction bits are then shipped to Bob via `send_int(bob, m_local)` and `send_int(bob, m_ent)`, each of which yields a `qnet.send_int` op with the corresponding bit as data and `@Bob` as remote. The *singular* form of the `send_int` operation is what gets emitted because the program is compiled with `singular_comm_ops=True`; with the default (`False`), the SDK would instead pack each bit into a one-element tensor and emit `qnet.send_ints` (the plural for, based on tensors), which would then be unfolded back into single-value ops at MIR level by `unfold-comm-ops`. See [Communication](../../sdk/communication.md) for that asymmetry.

The program closes with `result = recv_int(bob)`, which records a `qnet.recv_int` op that will block at runtime until Bob sends back a single classical value. In this example the value is not actually used — it just keeps Alice alive long enough for Bob to finish before her process exits.

## Compile

```python
_, hir = teleport.compile(singular_comm_ops=True)
print(str(hir))
```

`compile()` returns `(return_value, QoalaModule)`. The decorated function returns `None`, so the first element is `None`; the second is the compiled module, and `str(...)` over it gives the textual HIR. The `singular_comm_ops=True` flag forces single-value classical ops in HIR — useful when you want the emitted HIR to map straight onto the downstream pipeline without the unfolding step.

## What HIR looks like

The emitted HIR (abbreviated and pretty-printed) looks roughly like:

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

(The actual SSA names will differ — that's just the shape.)

## Take it through the rest of the pipeline

See [Continuing the pipeline](../../continuing-pipeline.md). For this program the recommended invocation is:

```sh
qoala-opt alice.hir.mlir \
  --qnet-peephole-optimizations \
  --qnet-dead-code-elimination \
  --lower-qoala-hir-to-mir \
  --lower-qoala-mir-to-lir \
| qoala-translate --mlir-to-iqoala > alice.iqoala
```
