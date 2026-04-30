# Architecture

`euqalyptus` is a thin layer that:

1. Lets you write a quantum-network program in Python.
2. Records every SDK call into an internal pseudo-AST.
3. Walks that AST to emit Qoala HIR — the dialect understood by [qoala-mlir](<QOALA_MLIR_DOCS_URL>).

The end-to-end picture is in [Overview](../overview.md). This section drills into the frontend internals.

- **[From Python to Qoala HIR](python-to-hir.md)** — what happens between `program.compile()` and a printable `module.asm`.

The structure of the package itself:

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

`tests/bindings/` is particularly useful when you need a sanity check that a particular SDK construct really lowers to a particular HIR shape — those tests exercise the full Python → HIR path and assert the textual output.
