# Teleportation — receiver

This is the program that runs on the node receiving the teleported state — here called **Bob**. It is taken verbatim from `qoala-compiler/examples/teleportation/bob.py`. Bob receives the two classical correction bits Alice sent, applies the conditional Z correction, and measures the recovered qubit. Unlike the [Sender](sender.md), this side exercises the SDK's branching machinery, since the Z correction is applied only when the corresponding correction bit is set at runtime.

## The program

```python
from euqalyptus import QoalaProgram
from euqalyptus.operations import Remote
from euqalyptus.types.quantum import Entangle, ScopedQubit
from euqalyptus.operations.communication import recv_int
from euqalyptus.operations.branching import if_cond
from euqalyptus.operations.control_flow import return_results


@QoalaProgram
def teleport():
    alice = Remote("Alice")
    q_ent = Entangle("Alice")
    x_corr = recv_int(alice)
    z_corr = recv_int(alice)
    with if_cond(z_corr == 1) as (t, f):
        cond_qubit = ScopedQubit(q_ent)
        with t:
            cond_qubit.Z()
            t.yield_value(cond_qubit)
    meas = cond_qubit.measure()
    return_results(meas)


if __name__ == "__main__":
    _, module = teleport.compile(singular_comm_ops=True)
    print(str(module))
```

## Walkthrough

The program opens the same way as the sender: `alice = Remote("Alice")` registers the remote-peer alias at module scope, and `q_ent = Entangle("Alice")` records a `qnet.eprs { remote = @Alice }` op that yields Bob's local half of the Bell pair Alice and Bob share.

The two subsequent `recv_int(alice)` calls record `qnet.recv_int` ops that will block at runtime until Alice has sent the corresponding correction bits. Their results are stored as `x_corr` and `z_corr` — note that in this minimal example only `z_corr` is actually used; the receive of `x_corr` is recorded for symmetry but the conditional X correction it would gate is left out. A fully faithful teleportation receiver would mirror the `if_cond(z_corr == 1)` block with an `if_cond(x_corr == 1)` block applying `cond_qubit.X()`.

The interesting part of the program is the conditional Z correction. The receiver enters a branching region with `with if_cond(z_corr == 1) as (t, f):`, where `t` is the "then" branch and `f` is the "else" branch. Inside the region — but before entering either branch — the program declares `cond_qubit = ScopedQubit(q_ent)`. This is the critical step: HIR's value-based semantics require every gate inside an `scf.if` to operate on a fresh SSA value, and the `scf.if` itself yields a *single* `!qnet.qubit` whose type and slot must be fixed *before* either arm is recorded. `ScopedQubit` captures `q_ent`, exposes the same qubit-method surface (`Z`, `X`, `measure`, …), and lets the front-end emit a well-formed `scf.if` no matter how complex the arms are.

Inside the `with t:` block, `cond_qubit.Z()` records a `qnet.z` on the captured original `q_ent`, and `t.yield_value(cond_qubit)` marks the wrapper as a value to be yielded out of the "then" region. The "else" branch is empty: the front-end automatically synthesizes a `scf.yield` carrying the unmodified `q_ent`, so both arms agree on the yielded type (`!qnet.qubit`). After the `with if_cond(...)` block exits, `cond_qubit` rebinds to the SCF result, so the subsequent `cond_qubit.measure()` records `qnet.measure` on that post-branch value rather than on either of the in-region SSA values.

Finally, `return_results(meas)` records `qnet.return %meas` so the i1 measurement outcome is the program's return value.

A consequence of `ScopedQubit`'s lock-on-exit behavior: any further SDK call on `cond_qubit` after the `with if_cond(...)` block — for example, the `measure()` call here — is routed to the post-branch SCF result, not to the originally captured `q_ent`. This is what makes the `with`-block idiom read naturally despite Python having no opinion on the branch.

## Compile

```python
_, hir = teleport.compile(singular_comm_ops=True)
print(str(hir))
```

The compile invocation is identical to the sender's: `compile(singular_comm_ops=True)` forces scalar HIR send ops (here irrelevant since Bob only receives) and returns `(return_value, QoalaModule)`. Because the entry function does not have an explicit `return` statement, the first element is `None`. The second is the compiled module — `str(...)` over it gives the textual HIR.

## What HIR looks like

The emitted HIR (abbreviated and pretty-printed) looks like:

```mlir
module {
  qnet.remote @Alice

  qnet.func @teleport() {
    %0 = qnet.eprs {remote = @Alice} : !qnet.qubit
    %1 = qnet.recv_int {remote = @Alice} : i32
    %2 = qnet.recv_int {remote = @Alice} : i32
    %c1_i32 = arith.constant 1 : i32
    %3 = arith.cmpi eq, %2, %c1_i32 : i32
    %4 = scf.if %3 -> (!qnet.qubit) {
      %6 = qnet.z %0 : !qnet.qubit
      scf.yield %6 : !qnet.qubit
    } else {
      scf.yield %0 : !qnet.qubit
    }
    %5 = qnet.measure %4 : i1
    qnet.return %5 : i1
  }
}
```

A few details worth noting. The "then" region of the `scf.if` records the `qnet.z` on the captured original `%0`, producing the in-region SSA value `%6`; the `scf.yield %6` makes that value the result of the "then" branch. The "else" region is the front-end-synthesized `scf.yield %0`, carrying the unmodified qubit. The `scf.if` itself yields a single `!qnet.qubit` (`%4`), and the post-branch `qnet.measure` consumes that SCF result, not either of the in-region values — which is exactly what HIR's linearity requires.

Note also that `%1` (the received but never-used `x_corr`) survives the HIR: `qnet.recv_int` is a network-communication op and is preserved by QDCE regardless of whether its result is consumed downstream, because eliding it would change the protocol-level structure observed by Alice (see the discussion of protocol correctness in the accompanying paper).

The `scf.if` itself does not survive the rest of the pipeline as-is. At HIR-to-MIR lowering, the yielded `!qnet.qubit` type is retyped to the `i32` qubit-pointer used by MIR but the `scf` structure is preserved. At MIR-to-LIR lowering, `scf` is rewritten into the unstructured `cf` dialect; the conditional becomes ordinary basic-block branches. Finally, the LIR-to-`.iqoala` backend reifies the surviving block arguments (those that the `scf.if` used to yield) into iQoala-level register copies via the `copy_cval` instruction — see the accompanying paper for the full mechanism.

## Take it through the rest of the pipeline

See [Continuing the pipeline](../../continuing-pipeline.md). The same invocation works for Bob as for Alice:

```sh
qoala-opt bob.hir.mlir \
  --qnet-peephole-optimizations \
  --qnet-dead-code-elimination \
  --lower-qoala-hir-to-mir \
  --lower-qoala-mir-to-lir \
| qoala-translate --mlir-to-iqoala > bob.iqoala
```

For the underlying branching mechanism — why `ScopedQubit` is necessary, how the front-end synthesizes the empty `else` arm, and how the backend reifies block arguments — see the implementation section of the accompanying paper. The branching test fixtures (`tests/bindings/test_branching.py`, `tests/syntax/test_branching_syntax.py`, `tests/semantics/test_branching.py`) exercise every corner case of the recording protocol.
