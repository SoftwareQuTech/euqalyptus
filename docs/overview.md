# Overview

`euqalyptus` is the Python-based frontend that lets you write a quantum-network program as ordinary Python and produce **Qoala HIR**, the highest-level intermediate representation of the Qoala compiler stack.

![Frontend pipeline](assets/figures/pipeline-overview.svg)

## Two ways to write a program

You can author a program in two equivalent shapes. The decorator form turns an ordinary function into a `QoalaProgram`:

```python
from euqalyptus import QoalaProgram

@QoalaProgram
def my_program():
    ...
```

The class-based form subclasses `QoalaProgramBase` and implements `main()`:

```python
from euqalyptus import QoalaProgramBase

class MyProgram(QoalaProgramBase):
    def main(self):
        ...
```

Both end up as the same kind of object internally; calling `.compile()` on either yields a `(return_value, QoalaModule)` tuple, where `QoalaModule.asm` is the textual Qoala HIR that you would pipe into [qoala-mlir](https://softwarequtech.github.io/qoala-mlir). See [SDK reference / Programs](sdk/programs.md) for the difference between the two patterns and when to pick which.

## What you can express

The SDK exposes a small surface that maps directly onto the operations supported by the QNet dialect of Qoala HIR. On the classical side there are the basic numeric types — `Int`, `Int32`, `UInt32`, `Bit`, `Float`, `Double` — together with the array variants `IntArray` and `FloatArray`. These behave like normal Python values inside a `@QoalaProgram` body but actually emit HIR ops behind the scenes. On the quantum side, `LocalQubit` constructs a locally initialized qubit, `EntangledQubit` (or the `Entangle()` factory) represents the local half of an EPR pair shared with a remote node, and `ScopedQubit` is a recording-time proxy used when a qubit must survive a conditional branching region.

Qubits support the usual single-qubit gates (`X`, `Y`, `Z`, `T`, `H`, `S`, the `rot_X/Y/Z` parameterized rotations), the two-qubit gates (`cnot`, `cz`, `cphase`), and measurement. The `Remote("Alice")` constructor declares a remote node by name, after which classical and entanglement operations targeting that node refer to it by that alias. Classical communication is available as `send_int`, `recv_int`, `send_float`, `recv_float`, plus their array (`send_ints`, `recv_ints`, …) variants. Control flow is shaped by `return_results(...)` to terminate the program, and by the `if_cond` family of context managers for runtime-conditional branching. The full reference is in [SDK reference](sdk/index.md).

## How the frontend produces HIR

When you call `.compile()`, the SDK turns your Python function into a QoalaHIR module in three logical steps, all carried out inside `euqalyptus/__init__.py`. First, a global `_compiler_lock` is acquired and a fresh `QoalaModule` is created — this gives the SDK a single piece of state to record into while it processes your function. Second, your decorated Python function is *executed*: SDK constructors such as `Int(10)`, `Entangle("Alice")`, and `q.measure()` do not perform the operation in the moment, but record AST nodes (`QoalaExpression`, `QoalaOperation`, …) into the module's current function body. Third, once the function returns, `QoalaModule.generate_qoala_hir()` walks the recorded AST and emits MLIR operations using the `qnet` Python bindings shipped by [qoala-mlir](https://softwarequtech.github.io/qoala-mlir).

The resulting module is reachable as `module.asm` (pretty-printed) or `module.generic_asm` (generic-form MLIR). For the deeper version of this story, see [Architecture / From Python to Qoala HIR](architecture/python-to-hir.md).

![Frontend internals](assets/figures/frontend-internals.svg)

## What happens after HIR

Once you have textual HIR, the rest of the pipeline lives in [qoala-mlir](https://softwarequtech.github.io/qoala-mlir):

```sh
qoala-opt program.hir.mlir \
    --qnet-peephole-optimizations \
    --qnet-dead-code-elimination \
    --lower-qoala-hir-to-mir \
    --lower-qoala-mir-to-lir \
| qoala-translate --mlir-to-iqoala > program.iqoala
```

See [Continuing the pipeline](continuing-pipeline.md) for the full handoff.
