# Figures to (re)draw

After triage, the docs site needs **three** figures — all of them can be exported directly from the accompanying paper's LaTeX source rather than redrawn from scratch. Drop the exported PDF/SVG into `docs/assets/figures/` under the filename listed below; the markdown references already point at those paths.

## `pipeline-overview.svg`

- **Referenced from:** `docs/index.md`, `docs/overview.md`.
- **Source:** Export from the paper's `fig:qoala-compiler-architecture` (the big TikZ overview in `compiler-paper/03-architecture/architecture.tex`). The same artifact is reused on the qoala-mlir docs site; the "euqalyptus span" highlight that the docs version once described is a CSS/visual emphasis concern rather than a separate diagram.

## `frontend-internals.svg`

- **Referenced from:** `docs/overview.md`, `docs/architecture/python-to-hir.md`.
- **Source:** Export from the paper's `fig:frontend` (the Python-interpreter → AST → HIR translation TikZ in `compiler-paper/03-architecture/architecture.tex`). The figure already shows the three stages the docs describe.

## `entanglement-flow.svg`

- **Referenced from:** `docs/sdk/remotes.md`, `docs/examples/teleportation/index.md`.
- **Source:** Export from the paper's `fig:intro` (the two-node EPR + classical-channel diagram in `compiler-paper/00-introduction/introduction.tex`). The teleportation correction-bit annotation referenced by the docs is a minor overlay on top of the same figure.

## Figures intentionally dropped

The following stubs were removed because the prose + code blocks on each page already carry the meaning; reintroduce them only if a future doc revision explicitly needs the visual:

- `program-models.svg` — `sdk/programs.md` already shows both the decorator and class-based code blocks side-by-side and includes a "When to use which" table.
- `qubit-lifecycle.svg` — `sdk/qubit-ops.md` describes the allocate-gate-measure lifecycle and the linearity property in prose.
- `compile-options.svg` — `sdk/compile.md` documents `compile_lazy` and `singular_comm_ops` with prose plus code examples for each.
