# Control flow

Source: `euqalyptus/operations/control_flow.py`.

## `return_results(...)` / `ReturnResults`

`return_results` (and the alias `ReturnResults`, which is the same callable) records a `qnet.return` op that terminates the current function. Use it to return classical values — typically measurement outcomes — from a Qoala program.

```python
from euqalyptus.operations.control_flow import return_results, ReturnResults

@QoalaProgram
def measure_and_return():
    q = LocalQubit()
    q.H()
    m = q.measure()
    return_results(m)
```

### Signatures

```python
ReturnResults()                # qnet.return
ReturnResults(x)               # qnet.return %x
ReturnResults(x, y, z)         # qnet.return %x, %y, %z
ReturnResults([x, y, z])       # same — lists/tuples are flattened
```

The variadic form accepts any number of `QoalaExpression`s, plus Python `int` / `float` literals (auto-promoted), and lists or tuples of the same.

### Implicit terminator

If you don't call `return_results(...)` at the end of your program, the SDK infers an empty return when emitting HIR. You only need to call it explicitly when you want to return one or more values, or when you need to terminate early (the latter is less common in HIR, since branching is handled separately).

## Branching

Branching constructs (`if_cond`, `if_eq`, `if_lt`, …) live in `euqalyptus.operations.branching`. They exist and are exercised in the test suite (`tests/bindings/test_branching.py`, `tests/syntax/test_branching_syntax.py`, `tests/semantics/test_branching.py`), but are intentionally **not documented here yet**. Refer to those tests if you need to use branching today; the documented surface here will be expanded in a future revision.

## API reference

::: euqalyptus.operations.control_flow
    options:
      members:
        - ReturnResults
        - return_results
