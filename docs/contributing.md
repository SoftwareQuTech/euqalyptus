# Contributing

## Set up your dev environment

For day-to-day development you want an editable install with the dev extras:

```sh
git clone <this repo>
cd qoala-compiler

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

The `[dev]` extra brings in `pytest`, `build`, `twine`, `pylint`, `mypy`, and `black`.

You also need a working [qoala-mlir](<QOALA_MLIR_DOCS_URL>) install — the SDK imports `qnet.dialects.qnet` and `qnet.ir` from it, and the bindings tests assert against the textual HIR it emits. Either:

- Install the `qoala-mlir` wheel from its [GitHub releases page](<QOALA_MLIR_RELEASES_URL>) into the same venv (`pip install https://.../qoala_mlir-<version>-...whl`), or
- Point `PYTHONPATH` at a local qoala-mlir build tree (see [qoala-mlir / Developer's guide / Building from source](<QOALA_MLIR_DOCS_URL>/developer-guide/build-from-source/)).

## Running the tests

```sh
pytest
```

The test suite lives in `tests/`:

```
tests/
├── bindings/        # full Python → HIR path; asserts on the emitted module
├── semantics/       # semantic checks: arrays, booleans, numeric, branching
├── syntax/          # SDK syntactic checks (errors raised by constructors)
├── programs/        # decorator vs class form, annotation handling
└── helpers_tests.py
```

Per the project conventions, prefer **lifting examples from the test suite or the `examples/` directory** when writing user-facing material — those programs are known to compile and emit valid HIR.

## Where to put new code

| Adding… | Goes in |
| --- | --- |
| A new operation visible to users | `src/euqalyptus/operations/<topic>.py` (factory) + `src/euqalyptus/ast/operations/<topic>.py` (AST node) |
| A new classical type | `src/euqalyptus/types/classical/<topic>.py` |
| A new quantum type or qubit method | `src/euqalyptus/types/quantum/qubit.py` |
| A new error class | `src/euqalyptus/errors.py` |
| A test exercising the full Python → HIR path | `tests/bindings/test_<feature>.py` |
| A unit test on AST construction only | `tests/semantics/` or `tests/syntax/` |

## Code style

The project uses `black` for formatting, `pylint` for linting, and `mypy` for type-checking. The `pyproject.toml` configures all three.

```sh
black src tests
pylint src
mypy src
```

`pylint` is configured strict (`fail-under = 10`); a few categories are disabled in `[tool.pylint."messages control"]` to keep the signal manageable.

## How euqalyptus relates to qoala-mlir

[qoala-mlir](<QOALA_MLIR_DOCS_URL>) provides the `qnet` Python bindings package that euqalyptus imports for HIR emission, plus the `qoala-opt` and `qoala-translate` binaries that consume the emitted HIR.

The contract:

- euqalyptus only depends on the `qnet.dialects.qnet` and `qnet.ir` Python modules. If those import paths change, the relevant call sites in `src/euqalyptus/module.py` (and a few AST emitters) need updates.
- The set of HIR ops euqalyptus emits is determined by `Dialect/QNet/QNetOps.td` in qoala-mlir. If a new op is added there, the corresponding AST emitter in `src/euqalyptus/ast/operations/` may need to be added or updated.
- New SDK constructs (e.g., a new qubit method) typically require:
  1. A method on `Qubit` in `src/euqalyptus/types/quantum/qubit.py`.
  2. A corresponding AST node in `src/euqalyptus/ast/operations/quantum.py`.
  3. The matching `qnet.<op>` builder call in the AST node's emit path.

When adding an op that doesn't exist in qoala-mlir yet, land the qoala-mlir change first (so the `qnet` Python builder exists), rebuild the bindings, then update euqalyptus to use it.

## Reporting issues / proposing changes

Open an issue with:

- A minimal `@QoalaProgram` snippet that reproduces the issue.
- The textual HIR you expect vs. what the SDK actually emits (`print(str(module))`).
- The version (or commit hash) of both euqalyptus and qoala-mlir you're running.

For new SDK features, a short note describing the user-facing surface (new types, new operations, expected HIR shape) helps reviewers a lot.
