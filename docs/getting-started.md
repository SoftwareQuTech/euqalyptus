# Getting started

This page covers the quickest path to writing a Qoala program: install a pre-built `euqalyptus` release and produce your first HIR module.

If you need to modify the SDK itself, see [Contributing](contributing.md) for the from-source dev install.

## Requirements

- **Python 3.10, 3.11, or 3.12.** Python 3.13 is **not supported** because the underlying `qoala-mlir` Python bindings depend on `numpy ≤ 1.26`, which itself does not support 3.13.
- A platform with a published `qoala-mlir` wheel (Linux x86-64 is the primary target).

## Install

`euqalyptus` depends on the `qoala-mlir` Python wheel for the `qnet` bindings and the `qoala-opt` / `qoala-translate` binaries. Both are published on the [qoala-mlir GitHub releases page](<QOALA_MLIR_RELEASES_URL>) — you install the qoala-mlir wheel from there first, then `euqalyptus` on top:

```sh
python3.11 -m venv .venv
source .venv/bin/activate

# 1. Install the qoala-mlir wheel from its GitHub release.
pip install https://github.com/<org>/qoala-mlir/releases/download/<version>/qoala_mlir-<version>-cp311-cp311-linux_x86_64.whl

# 2. Install euqalyptus.
pip install euqalyptus
```

The exact qoala-mlir wheel filename depends on the Python version and platform; pick the one that matches your interpreter from the release page. See [the qoala-mlir Getting started](<QOALA_MLIR_DOCS_URL>/getting-started/) for the full list of supported platforms and the from-source path if no wheel is available.

## Your first program

Save this as `hello.py`:

```python
from euqalyptus import QoalaProgram
from euqalyptus.operations import Remote
from euqalyptus.types.quantum import Entangle
from euqalyptus.operations.communication import send_int

@QoalaProgram
def hello():
    alice = Remote("Alice")
    q = Entangle("Alice")
    m = q.measure()
    send_int(alice, m)

if __name__ == "__main__":
    _, module = hello.compile()
    print(str(module))
```

Run it:

```sh
python hello.py
```

You should see textual Qoala HIR (a `module { … }` block with `qnet.*` ops) printed on stdout.

## Compile options

`compile()` accepts two boolean keyword arguments (see [SDK reference / Compilation](sdk/compile.md)):

- `compile_lazy=True` — skip the final HIR emission. Useful when you only want to inspect the internal AST built by the SDK; the returned module will not have `.asm` populated until you call `.generate_qoala_hir()` yourself.
- `singular_comm_ops=True` — emit single-value `send_int`/`recv_int`/`send_float`/`recv_float` ops instead of their tensor-typed multi-value counterparts. This avoids tensor lowering downstream and can simplify the optimizer's job.

```python
_, module = hello.compile(singular_comm_ops=True)
```

## Where to go next

- Read a complete worked example: [Examples / Teleportation](examples/teleportation/index.md).
- Look up a specific SDK construct: [SDK reference](sdk/index.md).
- Understand how the SDK calls become MLIR ops: [Architecture / From Python to Qoala HIR](architecture/python-to-hir.md).
- Take HIR through the rest of the pipeline: [Continuing the pipeline](continuing-pipeline.md).
- Modify the SDK itself: [Contributing](contributing.md).
