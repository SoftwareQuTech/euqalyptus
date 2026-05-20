# Continuing the pipeline

Once `module.asm` is populated, you have handed off the program to the [qoala-mlir](https://softwarequtech.github.io/qoala-mlir) toolchain. This page is a thin pointer guide — for the authoritative description of `qoala-opt`, every pass, and every flag, see the [qoala-mlir docs](https://softwarequtech.github.io/qoala-mlir).

## The handoff

Two patterns are equally common. The first writes the module to disk and then drives the toolchain externally:

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

The second pipes the textual HIR directly into `qoala-opt`'s stdin from Python:

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

If your program uses send/recv and you do not pass `singular_comm_ops=True` to `compile()`, the emitted HIR contains tensor-typed multi-value comm ops (`qnet.send_ints`, and the receive variants emitted by their tensor-form callers). At MIR level, `unfold-comm-ops` rewrites them to single-value form, so you do not need to do anything extra unless you are trying to keep the tensor form for some reason — in which case use `--lower-qoala-mir-to-lir=disable-unfold-comm-ops=true`. If you do pass `singular_comm_ops=True`, the HIR is already in single-value form on the send side and the unfold pass is effectively a no-op for those ops.

## Cost-model knobs and analyses

Some passes — the analysis-print passes and the MILP block reorderer — consume cost-model parameters via top-level flags on `qoala-opt`:

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

The full table is in [qoala-mlir / Tools / qoala-opt](https://softwarequtech.github.io/qoala-mlir/tools/qoala-opt/). These flags affect the analyses' numbers and the MILP objective; they do not affect lowering correctness.

## Inspecting intermediate IRs

Several upstream `mlir-opt` flags are also accepted by `qoala-opt` and are useful when you want to see what each pass produced. `--print-ir-after=lower-qoala-hir-to-mir` dumps the MIR right after the HIR-to-MIR conversion; `--print-ir-after-all` dumps after every pass; and `--mlir-print-op-generic` prints in generic form, which is handy when debugging custom verifiers. See [qoala-mlir / Tools / qoala-opt / Standard MLIR knobs](https://softwarequtech.github.io/qoala-mlir/tools/qoala-opt/#standard-mlir-knobs).

## Going further

For a deep dive into what each pass does, see [qoala-mlir / Passes reference](https://softwarequtech.github.io/qoala-mlir/passes/). For the architecture of the pipeline, see [qoala-mlir / Architecture / The three IRs](https://softwarequtech.github.io/qoala-mlir/architecture/irs/).
