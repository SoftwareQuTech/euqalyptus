# Overview

`euqalyptus` is the Python-based frontend that lets you write a quantum-network program as ordinary Python and produce **Qoala HIR**, the highest-level intermediate representation of the Qoala compiler stack.

![Frontend pipeline](assets/figures/pipeline-overview.svg)

## Two ways to write a program

Either decorate a function:

```python
from euqalyptus import QoalaProgram

@QoalaProgram
def my_program():
    ...
```

…or subclass `QoalaProgramBase` and implement `main()`:

```python
from euqalyptus import QoalaProgramBase

class MyProgram(QoalaProgramBase):
    def main(self):
        ...
```

Both end up as the same kind of object internally. Calling `.compile()` on either yields a `(return_value, QoalaModule)` tuple. `QoalaModule.asm` is the textual Qoala HIR that you'd pipe into [qoala-mlir](<QOALA_MLIR_DOCS_URL>).

See [SDK reference / Programs](sdk/programs.md) for the difference between the two patterns and when to pick which.

## What you can express

The SDK exposes:

- **Classical types** — `Int`, `Int32`, `UInt32`, `Bit`, `Float`, `Double`, `IntArray`, `FloatArray`. These behave like normal Python values inside a `@QoalaProgram` body but actually emit HIR ops behind the scenes.
- **Quantum types** — `LocalQubit`, `EntangledQubit`, `ScopedQubit`, plus the `Entangle()` factory.
- **Qubit operations** — single-qubit gates (`X`, `Y`, `Z`, `T`, `H`, `K`, `S`, `rot_X/Y/Z`), two-qubit gates (`cnot`, `cz`, `cphase`), measurement and free.
- **Remotes** — `Remote("Alice")` declares a remote node by name; subsequent classical and entanglement ops reference it.
- **Communication** — `send_int`, `recv_int`, `send_float`, `recv_float`, plus their array (`send_ints`, `recv_ints`, …) variants.
- **Control flow** — `return_results(...)` to terminate the program.

The full reference is in [SDK reference](sdk/index.md).

## How the frontend produces HIR

When you call `.compile()`, three things happen, all in `euqalyptus/__init__.py`:

1. A global `_compiler_lock` is acquired and a fresh `QoalaModule` is created.
2. Your decorated Python function is **executed**. The SDK constructors (`Int(10)`, `Entangle("Alice")`, `q.measure()`, …) don't perform the operation — they record AST nodes (`QoalaExpression`, `QoalaOperation`, …) into the module's current function body.
3. After the function returns, `QoalaModule.generate_qoala_hir()` walks the AST and emits MLIR operations using the `qnet` Python bindings shipped by [qoala-mlir](<QOALA_MLIR_DOCS_URL>).

The resulting module is reachable as `module.asm` (pretty-printed) or `module.generic_asm` (generic-form MLIR).

For more, see [Architecture / From Python to Qoala HIR](architecture/python-to-hir.md).

![Frontend internals](assets/figures/frontend-internals.svg)

## What happens after HIR

Once you have textual HIR, the rest of the pipeline lives in [qoala-mlir](<QOALA_MLIR_DOCS_URL>):

```sh
qoala-opt program.hir.mlir \
    --qnet-peephole-optimizations \
    --qnet-dead-code-elimination \
    --lower-qoala-hir-to-mir \
    --lower-qoala-mir-to-lir \
| qoala-translate --mlir-to-iqoala > program.iqoala
```

See [Continuing the pipeline](continuing-pipeline.md) for the full handoff.
