# Branching

Runtime-conditional control flow inside a `@QoalaProgram` body is expressed through the `if_cond` family of context managers. Each construct opens a branching region whose body is selected at runtime based on a boolean `QoalaExpression`. The region is emitted as an `scf.if` in HIR.

Source: `euqalyptus/operations/branching.py`.

## Importing

```python
from euqalyptus.operations.branching import (
    if_cond,
    if_eq, if_neq,
    if_lt, if_le,
    if_gt, if_ge,
)
```

The corresponding class-style names (`IfCondition`, `IfEq`, `IfNeq`, `IfLt`, `IfLe`, `IfGt`, `IfGe`) are also exported and behave identically.

## Branching operators

| Construct | Signature | Records |
| --- | --- | --- |
| `if_cond(condition)` | `(QoalaExpression\|bool) -> ConditionalBranching` | `scf.if` gated on the boolean expression |
| `if_eq(lhs, rhs)` | two-operand comparison | `scf.if` gated on `EqualsOp(lhs, rhs)` |
| `if_neq(lhs, rhs)` | two-operand comparison | `scf.if` gated on `NotEqualsOp(lhs, rhs)` |
| `if_lt(lhs, rhs)` | two-operand comparison | `scf.if` gated on `LessThanOp(lhs, rhs)` |
| `if_le(lhs, rhs)` | two-operand comparison | `scf.if` gated on `LessThanOrEqualsOp(lhs, rhs)` |
| `if_gt(lhs, rhs)` | two-operand comparison | `scf.if` gated on `GreaterThanOp(lhs, rhs)` |
| `if_ge(lhs, rhs)` | two-operand comparison | `scf.if` gated on `GreaterThanOrEqualsOp(lhs, rhs)` |

The two-operand variants are pure conveniences for the very common case of comparing a value against another value or a literal; they are exactly equivalent to wrapping the comparison in `if_cond(lhs OP rhs)` but keep the comparison as an explicit AST node that downstream rewrites can match on.

Comparison operands may be `QoalaIntegerType`, `QoalaFloatingPointType`, or Python `int` / `float` literals (which are auto-promoted via `QoalaNumericValue.from_immediate`).

## The `with` idiom

Every branching construct is used as a context manager. The condition is evaluated at runtime, and the `as (t, f)` clause binds two handles representing the "then" and "else" arms. Each arm is itself a context manager that is entered separately:

```python
with if_cond(z_corr == 1) as (t, f):
    cond_qubit = ScopedQubit(q_ent)
    with t:
        cond_qubit.Z()
        t.yield_value(cond_qubit)
    # `with f:` is optional; if omitted, the front-end synthesises
    # an empty else arm that yields the unmodified scoped values.
```

Two rules to keep in mind:

1. **Declare scoped wrappers before entering either arm.** Any value that must survive the branch — a qubit threaded through a conditional gate, a classical register that may be updated only in one arm — has to be wrapped in [`ScopedQubit`](types-quantum.md#scopedqubit) or [`ScopedVar`](types-classical.md#scopedvar) at the top of the `with if_cond(...)` body, *before* `with t:` or `with f:` is entered. This is what lets the front-end fix the result types of the underlying `scf.if` ahead of time.
2. **Yield the scoped wrapper from each arm that touched it.** Inside an arm, call `t.yield_value(cond_qubit)` (or `f.yield_value(...)`) to mark the wrapper as a value to be yielded out of that region. Any arm that does not call `yield_value` will yield the unmodified original captured by the wrapper.

After the `with if_cond(...)` block exits, the scoped wrappers re-bind to the SCF result, so subsequent SDK calls (`cond_qubit.measure()`, etc.) act on the post-branch value rather than on either of the in-region SSA values.

For a fully worked example using `if_cond`, `ScopedQubit`, and the `with t:` / `with f:` arms, see the [Teleportation receiver](../examples/teleportation/receiver.md) walkthrough.

## Errors

| Exception | Raised when |
| --- | --- |
| `NotBooleanArgumentError` | The `if_cond(...)` argument cannot evaluate to a `QoalaBool`. |
| `OperandMismatchError` | A two-operand branching construct receives fewer than two operands. |

## What ends up in HIR

A minimal use of `if_cond`:

```python
@QoalaProgram
def conditional_z():
    alice = Remote("Alice")
    q_ent = Entangle("Alice")
    z_corr = recv_int(alice)
    with if_cond(z_corr == 1) as (t, f):
        cond_qubit = ScopedQubit(q_ent)
        with t:
            cond_qubit.Z()
            t.yield_value(cond_qubit)
    meas = cond_qubit.measure()
    return_results(meas)
```

becomes (sketched):

```mlir
module {
  qnet.remote @Alice
  %ent = qnet.eprs { remote = @Alice } : !qnet.qubit
  %z   = qnet.recv_int { remote = @Alice } : i32
  %one = arith.constant 1 : i32
  %c   = arith.cmpi eq, %z, %one : i1
  %ent2 = scf.if %c -> (!qnet.qubit) {
    %ent_z = qnet.z %ent : !qnet.qubit
    scf.yield %ent_z : !qnet.qubit
  } else {
    scf.yield %ent : !qnet.qubit
  }
  %m = qnet.measure %ent2 : i1
  qnet.return %m : i1
}
```

## API reference

::: euqalyptus.operations.branching
    options:
      members:
        - IfCondition
        - IfEq
        - IfNeq
        - IfLt
        - IfLe
        - IfGt
        - IfGe
        - if_cond
        - if_eq
        - if_neq
        - if_lt
        - if_le
        - if_gt
        - if_ge
