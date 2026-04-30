# From Python to Qoala HIR

What `program.compile()` does, in three stages.

![Frontend internals](../assets/figures/frontend-internals.svg)

## Stage 1: Setup

`QoalaProgram.compile(...)` (in `euqalyptus/__init__.py`):

1. Acquires the global `_compiler_lock`. Only one program can be compiling at a time.
2. Sets `QoalaProgram._instance = self` so the user-facing constructors can find the active program.
3. Resets `QoalaProgram._declared_remotes` and creates a fresh `CompilationContext` (which captures the `compile_lazy` and `singular_comm_ops` flags).
4. Clears the program's `QoalaModule` and adds a single function (named after the entry function — typically `my_program` or `main`).

After this, the SDK is in *recording mode*.

## Stage 2: Recording

Now your Python function runs:

```python
@QoalaProgram
def example():
    Remote("Alice")
    q = Entangle("Alice")
    m = q.measure()
    send_int("Alice", m)
```

But every SDK call is *intercepted*:

- `Remote("Alice")` ends up in `euqalyptus.operations.Remote.__new__`, which either returns the existing `DeclaredRemote` for that name or constructs a new one.
- `Entangle("Alice")` is a function (not a class) defined in `euqalyptus/types/quantum/qubit.py`. It checks that the remote was declared and produces an `EntangledQubit`, which is itself a `QoalaEprs` AST node.
- `q.measure()` — `Qubit.measure` calls `QoalaEprs.measure`, which records a `qnet.measure`-shaped AST node into the active function's body and returns a `QoalaInteger` AST.
- `send_int("Alice", m)` — the `SendInt` factory in `euqalyptus/operations/communication.py` wraps the AST node `m` plus the remote name into a `SendIntOp` AST node, again pushed into the current function body.

The function then returns. Its return value (often `None`) is captured.

The pseudo-AST built up during recording is structured the same way the HIR will be:

- `QoalaModule` contains `QoalaFunction`s.
- Each `QoalaFunction` has a body that is a list of `QoalaOperation`s.
- `QoalaOperation`s reference `QoalaExpression` operands and produce `QoalaRuntimeValue`s.

You can see this state by passing `compile_lazy=True` to `compile()`: the AST is built, but Stage 3 is skipped.

## Stage 3: Emission

If `compile_lazy=False` (the default), `compile()` calls `module.generate_qoala_hir()`. That walks the AST and, for each operation, calls into the `qnet.dialects.qnet` Python builders shipped by [qoala-mlir](<QOALA_MLIR_DOCS_URL>/bindings/) to emit the corresponding MLIR op.

The relevant imports inside `module.py`:

```python
from qnet.dialects import qnet
from qnet.ir import Module, Context, Location, InsertionPoint
```

The emission does roughly:

```python
with Context() as ctx, Location.unknown():
    self._qir_module = Module.create()
    with InsertionPoint(self._qir_module.body):
        # Emit qnet.remote ops for each declared remote.
        for r in self._remotes:
            qnet.remote(name=r.name)
        # Emit a qnet.func wrapping each function.
        for fn in self._functions:
            self._emit_function(fn)
```

After `generate_qoala_hir()` returns, the `_qir_module` is populated and `module.asm` returns its pretty-printed form via `_qir_module.operation.get_asm()`.

## Stage 4: Teardown

Back in `compile()`:

5. The remotes accumulated in `_declared_remotes` are stored on `module.remotes`.
6. `_is_compiled` is flipped to `True`.
7. `QoalaProgram._instance` is deleted.
8. The lock is released.

The returned tuple is `(return_value_from_user_function, the_module)`.

## What "branching is intercepted" means in practice

A `with if_cond(m == 1) as (t, f):` block in user code creates a `ConditionalBranching` AST node, then enters context-manager state that swaps the "current function body" to a sub-list. Anything you do inside the `with` body gets recorded into that sub-list. Exiting the context manager pops back to the parent body.

This is why the SDK *can* support runtime-conditional control flow with what looks like ordinary Python `with` blocks: the whole thing is a recording protocol, not real control flow.

This page does not document the branching ops in detail; see the source under `euqalyptus/operations/branching.py` and the tests under `tests/bindings/test_branching.py` if you need them now.

## Why a global lock?

The recording protocol relies on a class-level slot (`QoalaProgram._instance`) that points to "the program currently being compiled." That slot is what lets `Remote("Alice")` know which program to declare the remote on. A global lock around `compile()` makes that single-instance invariant safe to assume during recording.

The implication is that **you cannot compile two `QoalaProgram`s concurrently** — calls serialize. For a CI/test loop this is rarely an issue; for a user-facing tool that needs parallelism, you'd have to refactor the recording state.
