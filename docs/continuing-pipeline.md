# Continuing the pipeline

Once `module.asm` is populated, you've handed off the program to the [qoala-mlir](<QOALA_MLIR_DOCS_URL>) toolchain. This page is a thin pointer guide — for the authoritative description of `qoala-opt`, every pass and flag, see the [qoala-mlir docs](<QOALA_MLIR_DOCS_URL>).

## The handoff

Two equally common patterns:

**Write to disk:**

```python
_, module = my_program.compile()
with open("program.hir.mlir", "w") as f:
    f.write(str(module))
```

```sh
qoala-opt program.hir.mlir \
  --qnet-peephole-optimizations \
  --qnet-dead-code-elimination \
  --lower-qoala-hir-to-mir \
  --lower-qoala-mir-to-lir \
  > program.lir.mlir

qoala-translate --mlir-to-iqoala program.lir.mlir > program.iqoala
```

**Pipe directly:**

```python
import subprocess
_, module = my_program.compile()
subprocess.run(
    ["qoala-opt",
     "--qnet-peephole-optimizations",
     "--qnet-dead-code-elimination",
     "--lower-qoala-hir-to-mir",
     "--lower-qoala-mir-to-lir"],
    input=str(module),
    text=True,
    check=True,
)
```

## A note on `singular_comm_ops`

If your program uses send/recv and you don't pass `singular_comm_ops=True`, the emitted HIR contains tensor-typed multi-value comm ops (`qnet.send_ints`, `qnet.recv_ints`). At MIR level, `unfold-comm-ops` rewrites them to single-value form. You don't need to do anything extra unless you're trying to keep the tensor form for some reason — in which case use `--lower-qoala-mir-to-lir=disable-unfold-comm-ops=true`.

If you do pass `singular_comm_ops=True`, the HIR is already in single-value form and the unfold pass is a no-op for those ops.

## Cost-model knobs and analyses

Some passes (analysis-print passes; the MILP block reorderer) consume cost-model parameters via top-level flags on `qoala-opt`:

```sh
qoala-opt program.hir.mlir \
  --qnet-peephole-optimizations \
  --lower-qoala-hir-to-mir \
  --lower-qoala-mir-to-lir \
  --qoalahost-add-block-precedences \
  --qoalahost-reorder-blocks=with-deadlines=true \
  --qoala-opt-single-gate-duration=8 \
  --qoala-opt-link-duration=2000 \
  --qoala-opt-program-horizon=10000
```

The full table is in [qoala-mlir / Tools / qoala-opt](<QOALA_MLIR_DOCS_URL>/tools/qoala-opt/). They affect the analyses' numbers and the MILP objective; they do not affect lowering correctness.

## Inspecting intermediate IRs

Useful flags from upstream `mlir-opt` (also accepted by `qoala-opt`):

- `--print-ir-after=lower-qoala-hir-to-mir` — dump MIR right after the HIR→MIR conversion.
- `--print-ir-after-all` — dump after every pass.
- `--mlir-print-op-generic` — print in generic form (handy when debugging custom verifiers).

See [qoala-mlir / Tools / qoala-opt / Standard MLIR knobs](<QOALA_MLIR_DOCS_URL>/tools/qoala-opt/#standard-mlir-knobs).

## Going further

For a deep dive into what each pass does, see [qoala-mlir / Passes reference](<QOALA_MLIR_DOCS_URL>/passes/). For the architecture of the pipeline, see [qoala-mlir / Architecture / The three IRs](<QOALA_MLIR_DOCS_URL>/architecture/irs/).
