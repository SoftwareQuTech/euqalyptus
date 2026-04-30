# Figures to (re)draw

Every entry below corresponds to an SVG stub under `docs/assets/figures/`. Each stub contains the figure title and a short description of the intended content; replace it one-for-one with your final asset (same filename, same path).

## `pipeline-overview.svg`

- **Referenced from:** `docs/index.md`, `docs/overview.md`.
- **Intended content:** Same end-to-end pipeline as the equivalent figure on the qoala-mlir docs site, but with the *euqalyptus frontend* span highlighted (user Python → AST → MLIR Python bindings → emitted Qoala HIR). The qoala-mlir part (HIR → MIR → LIR → .iqoala) is shown collapsed/dimmed.

## `frontend-internals.svg`

- **Referenced from:** `docs/overview.md`, `docs/architecture/python-to-hir.md`.
- **Intended content:** Three-stage diagram, left to right: (1) user Python with `@QoalaProgram` and SDK calls; (2) pseudo-AST recording inside `QoalaModule` (showing `DeclaredRemote`, `QoalaEprs`, `MeasureOp`, `SendIntOp`, etc.); (3) MLIR emission via `qnet.dialects.qnet` and `qnet.ir.{Module,Context,InsertionPoint}`. Annotate arrows with the relevant method (`compile()`, `generate_qoala_hir()`).

## `program-models.svg`

- **Referenced from:** `docs/sdk/programs.md`.
- **Intended content:** Side-by-side comparison of the two ways to declare a program: decorator (`@QoalaProgram` on a free function) vs. inheritance (`class X(QoalaProgramBase)` with a `main` method). Both arrows converge into the same `QoalaModule`. Note the `__new__` quirk in the inheritance branch (instances are `QoalaProgram`, not `QoalaProgramBase`).

## `qubit-lifecycle.svg`

- **Referenced from:** `docs/sdk/qubit-ops.md`.
- **Intended content:** Lifecycle of a `LocalQubit` as a left-to-right state machine: allocate → apply gates → optional two-qubit interaction → measure → optional free. Each step labeled with its emitted HIR op. Highlight the linearity arrow: after `measure`, the qubit value is consumed and any further use becomes a verifier error in `qnet-check-linear`.

## `entanglement-flow.svg`

- **Referenced from:** `docs/sdk/remotes.md`, `docs/examples/teleportation/index.md`.
- **Intended content:** Two-node diagram (Alice on the left, Bob on the right), each running its own Qoala program. An "EPR pair" arrow connects the two `Entangle` calls; a "classical channel" arrow carries `send_int`/`recv_int` traffic. The teleportation example specifically shows two correction bits flowing from Alice to Bob over the classical channel.

## `compile-options.svg`

- **Referenced from:** `docs/sdk/compile.md`.
- **Intended content:** Decision tree showing how the two boolean compile options change the emitted artifact: `compile_lazy` (stop after pseudo-AST vs. continue to MLIR emission), `singular_comm_ops` (single-value comm ops vs. tensor-typed multi-value comm ops, the latter unfolded at MIR level by `unfold-comm-ops`). Small inset code blocks show the resulting HIR shape in each combination.
