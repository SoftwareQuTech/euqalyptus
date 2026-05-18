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

If this is your first encounter with `euqalyptus`, read the [Overview](overview.md) for a sketch of the pipeline and follow [Getting started](getting-started.md) to set up your environment. The [Examples / Teleportation](examples/teleportation/index.md) tutorial walks through a runnable end-to-end program. When you start writing your own programs, the [SDK reference](sdk/index.md) is the place to look up types, qubit methods, and operations. The [Architecture / From Python to Qoala HIR](architecture/python-to-hir.md) page explains, in detail, what happens between your Python source and the emitted MLIR module — that is what every SDK call ultimately boils down to. Once you have a compiled HIR module in hand, [Continuing the pipeline](continuing-pipeline.md) hands you off to the [qoala-mlir](<QOALA_MLIR_DOCS_URL>) toolchain that takes it the rest of the way.

## What lives where

| You want to… | Go to |
| --- | --- |
| Write your first program | [Getting started](getting-started.md), [Examples](examples/index.md) |
| Look up a type or operation | [SDK reference](sdk/index.md) |
| Understand how `compile()` works | [SDK reference / Compilation](sdk/compile.md), [Architecture](architecture/python-to-hir.md) |
| Move from HIR to a runnable `.iqoala` | [Continuing the pipeline](continuing-pipeline.md), [qoala-mlir docs](<QOALA_MLIR_DOCS_URL>) |
| Contribute / set up locally | [Contributing](contributing.md) |
