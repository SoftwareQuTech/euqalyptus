# Teleportation — receiver

!!! info "TODO"
    The receiver side of teleportation requires applying corrections that depend on the **runtime values** of two classical bits received from the sender. In the current SDK, that needs the branching operators (`with if_cond(z_corr == 1) as (t, f): ...`), and **branching is intentionally not yet documented**.

    The runnable receiver program lives in [`qoala-compiler/teleportation/bob.py`](https://gitlab.tudelft.nl/qoala/qoala-compiler/-/blob/master/teleportation/bob.py) (resolve to your local checkout). Its current text is:

    ```python
    from euqalyptus import QoalaProgram
    from euqalyptus.operations import Remote
    from euqalyptus.types.quantum import Entangle, ScopedQubit
    from euqalyptus.operations.branching import if_cond
    from euqalyptus.operations.communication import recv_int
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
    ```

    A future revision of this documentation will cover branching (`if_cond`, `if_eq`, `if_lt`, …) and walk through this program in the same depth as the [Sender](sender.md) page.

    For the [Sender](sender.md), the doc is complete.

## Where to read more in the meantime

- The branching test fixtures: `tests/bindings/test_branching.py`, `tests/syntax/test_branching_syntax.py`, `tests/semantics/test_branching.py`.
- The deterministic teleportation variant in the repo (which avoids branching by always applying both corrections): under `qoala-compiler/bqc-with-teleport-deterministic/`.

When branching is documented, this page will be replaced with a full walkthrough.
