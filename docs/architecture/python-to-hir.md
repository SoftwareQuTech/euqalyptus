# From Python to Qoala HIR

When you call `program.compile()`, the SDK turns your Python function into a QoalaHIR module in four conceptually distinct stages, all carried out inside the body of `compile()` defined in `euqalyptus/__init__.py`.

![Frontend internals](../assets/figures/frontend-internals.svg)

## Stage 1: setup

`compile()` first acquires the global `_compiler_lock`. The recording protocol used in the next stage relies on a class-level slot, `QoalaProgram._instance`, that points to whatever program is currently being compiled, and that slot is what lets user-facing constructors like `Remote("Alice")` know which program to declare a remote on. The global lock keeps that single-instance invariant safe; the trade-off is that two `QoalaProgram` instances cannot be compiled concurrently from the same process — calls serialize. For a typical CI loop this is transparent; only a tool that wants parallel compilation would need to refactor that state.

Once the lock is held, `compile()` sets `QoalaProgram._instance` to `self`, resets the class-level `_declared_remotes` cache, and constructs a fresh `CompilationContext` that captures some compilation options, like `compile_lazy` and `singular_comm_ops`. It also clears the program's `QoalaModule` and adds a single function to it, named after the entry function — typically `my_program` for the decorator form or `main` for the class-based form. By the time stage 1 ends, the SDK is in *recording mode*.

## Stage 2: recording

Now your Python function runs. From Python's perspective nothing unusual happens — the interpreter walks the body once, executes each line *without executing the semantics of it*, and returns whatever the function returned. The semantic-less execution is important since every SDK call along the way is intercepted by a constructor or context manager that records an AST node into the active function body instead of performing its nominal action immediately. This effectively helps building the AST without executing what the SDK user wants to run.

```python
@QoalaProgram
def example():
    Remote("Alice")
    q = Entangle("Alice")
    m = q.measure()
    send_int("Alice", m)
```

When this body runs, `Remote("Alice")` reaches `euqalyptus.operations.Remote.__new__`, which either returns the existing `DeclaredRemote` for `"Alice"` or constructs a new one — so calling `Remote("Alice")` twice yields the same object. `Entangle("Alice")` is a factory function (defined in `euqalyptus/types/quantum/qubit.py`) that checks the remote is declared and produces an `EntangledQubit`, itself a `QoalaEprs` AST node. The subsequent `q.measure()` reaches `Qubit.measure`, which in turn calls `QoalaEprs.measure`, records a `qnet.measure`-shaped AST node into the function body, and returns a `QoalaInteger` AST. Finally, `send_int("Alice", m)` flows through the `SendInts` factory in `euqalyptus/operations/communication.py` (recall that `send_int` is an alias of the variadic `SendInts` — single-value scalar HIR sends are emitted only under `compile(singular_comm_ops=True)`), which wraps the AST node `m` and the remote name into a send op and pushes it into the current function body.

The pseudo-AST built up this way is structured exactly like the HIR will be: a `QoalaModule` contains `QoalaFunction`s; each `QoalaFunction` has a body that is an ordered list of `QoalaOperation`s; and each `QoalaOperation` references `QoalaExpression` operands and produces `QoalaRuntimeValue`s. You can inspect this state directly by passing `compile_lazy=True` to `compile()` — the AST is built but stage 3 is skipped, so what you get back is the recorded structure without any MLIR emission.

## Stage 3: emission

If `compile_lazy=False` (the default), `compile()` calls `module.generate_qoala_hir()`. That walks the AST and emits the corresponding MLIR ops using the `qnet` Python builders shipped by [qoala-mlir](https://softwarequtech.github.io/qoala-mlir/bindings/), so each AST node maps to a builder call in the `qnet` dialect:

```python
from qnet.dialects import qnet
from qnet.ir import Module, Context, Location, InsertionPoint
```

Concretely, `generate_qoala_hir()` creates an MLIR `Module` inside a fresh `Context`, then emits a `qnet.remote` declaration for each previously recorded remote and a `qnet.func` wrapping each recorded function:

```python
with Context() as ctx, Location.unknown():
    self._qir_module = Module.create()
    with InsertionPoint(self._qir_module.body):
        for r in self._remotes:
            qnet.remote(name=r.name)
        for fn in self._functions:
            self._emit_function(fn)
```

After this returns, the module's `asm` property pretty-prints the MLIR via `_qir_module.operation.get_asm()`.

## Stage 4: teardown

The final stage of `compile()` is bookkeeping. The remotes accumulated in `_declared_remotes` are copied onto `module.remotes`, the program's `_is_compiled` flag is flipped to `True`, the class-level `QoalaProgram._instance` is cleared, and the global lock is released. The call returns `(return_value_from_user_function, the_module)`.

## What branching interception looks like in practice

A `with if_cond(m == 1) as (t, f):` block in user code does not run real Python control flow over a quantum-network value. What it actually does is record a `ConditionalBranching` AST node and enter context-manager state that swaps the "current function body" pointer to a sub-list. Anything recorded inside the `with` body lands in that sub-list; exiting the context manager pops back to the parent body. The user-visible Python control flow is therefore a recording protocol — the actual branch lives in the recorded AST and shows up downstream as an `scf.if` in HIR.

This page does not document the branching ops in detail; for that, see the source under `euqalyptus/operations/branching.py` and the tests under `tests/bindings/test_branching.py`.
