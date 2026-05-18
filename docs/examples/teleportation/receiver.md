# Teleportation — receiver

!!! info "TODO"
    The receiver side of teleportation requires applying corrections that depend on the **runtime values** of two classical bits received from the sender. In the current SDK, that needs the branching operators (`with if_cond(z_corr == 1) as (t, f): ...`); the branching mechanism is now documented end-to-end in the accompanying paper, but the dedicated walkthrough page that mirrors the [Sender](sender.md) one is still to be written.

    The runnable receiver program lives in [`qoala-compiler/examples/teleportation/bob.py`](https://gitlab.tudelft.nl/qoala/qoala-compiler/-/blob/master/examples/teleportation/bob.py). Its current text is:

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

    A future revision of this page will cover the SDK-level branching API (`if_cond`, `if_eq`, `if_lt`, …) and walk through this program in the same depth as the [Sender](sender.md) page. The [Sender](sender.md) page is complete in the meantime.

## Where to read more in the meantime

The cheapest way to see the branching mechanism in action is the test suite: `tests/bindings/test_branching.py` exercises the full Python-to-HIR path, while `tests/syntax/test_branching_syntax.py` and `tests/semantics/test_branching.py` cover the static checks.

When branching is documented here, this page will be replaced with a full walkthrough.
