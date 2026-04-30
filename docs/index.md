# euqalyptus

`euqalyptus` is the Python frontend of the Qoala compiler stack. You write a quantum-network program as a regular Python function (or class), call `compile()`, and out comes a Qoala HIR module — the highest-level intermediate representation, which is then consumed by the [qoala-mlir](<QOALA_MLIR_DOCS_URL>) toolchain for the rest of the pipeline.

```python
from euqalyptus import QoalaProgram
from euqalyptus.operations import Remote
from euqalyptus.types.quantum import Entangle
from euqalyptus.operations.communication import send_int

@QoalaProgram
def hello_alice():
    alice = Remote("Alice")
    q = Entangle("Alice")
    m = q.measure()
    send_int(alice, m)

if __name__ == "__main__":
    _, hir = hello_alice.compile()
    print(str(hir))
```

![Frontend pipeline](assets/figures/pipeline-overview.svg)

## Where to start

- New here? Read the [Overview](overview.md) and follow [Getting started](getting-started.md).
- Want a runnable example? See [Examples / Teleportation](examples/teleportation/index.md).
- Looking up a type, qubit method, or operation? Jump to the [SDK reference](sdk/index.md).
- Curious about the path from Python to MLIR? See [Architecture / From Python to Qoala HIR](architecture/python-to-hir.md).
- After compilation, your HIR is fed to [qoala-mlir](<QOALA_MLIR_DOCS_URL>) — see [Continuing the pipeline](continuing-pipeline.md).

## What lives where

| You want to… | Go to |
| --- | --- |
| Write your first program | [Getting started](getting-started.md), [Examples](examples/index.md) |
| Look up a type or operation | [SDK reference](sdk/index.md) |
| Understand how `compile()` works | [SDK reference / Compilation](sdk/compile.md), [Architecture](architecture/python-to-hir.md) |
| Move from HIR to a runnable `.iqoala` | [Continuing the pipeline](continuing-pipeline.md), [qoala-mlir docs](<QOALA_MLIR_DOCS_URL>) |
| Contribute / set up locally | [Contributing](contributing.md) |
