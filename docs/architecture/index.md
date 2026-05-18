# Architecture

`euqalyptus` is a thin layer that lets you write a quantum-network program in Python, records every SDK call into an internal pseudo-AST while your function executes, and then walks that AST to emit Qoala HIR — the dialect understood by [qoala-mlir](<QOALA_MLIR_DOCS_URL>). The end-to-end picture is in the [Overview](../overview.md); this section drills into the frontend internals, starting with [From Python to Qoala HIR](python-to-hir.md), which walks through exactly what happens between `program.compile()` and a printable `module.asm`.

The structure of the package itself mirrors that pipeline. The top-level `__init__.py` defines `QoalaProgram`, `QoalaProgramBase`, and the `compile()` entry point. `module.py` holds the `QoalaModule` class and the MLIR-emission machinery. The internal pseudo-AST that `compile()` records into lives under `ast/`, with its core types in `model.py`, `value.py`, and `qubit.py`, and one AST-node file per operation kind under `ast/operations/`. The user-facing surface — the constructors and factories that intercept SDK calls during recording — sits in `operations/` (for things like `Remote` and `send_int`) and `types/` (split between `classical/` and `quantum/`). The remaining files cover support concerns (`utils/debug_info.py`, `errors.py`).

```
qoala-compiler/
├── src/euqalyptus/
│   ├── __init__.py             # QoalaProgram, QoalaProgramBase, compile()
│   ├── module.py               # QoalaModule and HIR emission
│   ├── ast/                    # internal pseudo-AST
│   │   ├── model.py
│   │   ├── value.py
│   │   ├── qubit.py
│   │   └── operations/         # AST nodes for every operation
│   ├── operations/             # user-facing operation factories (Remote, send_int, …)
│   ├── types/                  # user-facing types
│   │   ├── classical/
│   │   └── quantum/
│   ├── utils/debug_info.py
│   └── errors.py
├── tests/                      # syntax, semantics, bindings, programs
└── examples/                   # standalone runnable scripts
```

`tests/bindings/` is particularly useful when you need a sanity check that a particular SDK construct really lowers to a particular HIR shape: those tests exercise the full Python-to-HIR path and assert the textual output, so they are the cheapest way to confirm that a given user-level snippet emits the IR you expect.
