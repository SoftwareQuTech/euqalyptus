# Paper and citation

The design behind `euqalyptus` — how the frontend records SDK calls into a
pseudo-AST and emits Qoala HIR, the branching mechanism, and how the frontend
fits into the broader compilation pipeline — is described in:

> Sacha Bernheim, Bart van der Vecht, Davide Ferrari, Diego Rivera and
> Stephanie Wehner. **A Multi-Level Compiler Pipeline for Qoala Quantum
> Internet Programs**. In *2026 IEEE International Conference on Quantum
> Software (QSW)*, pages 12–24, Sydney, Australia, July 2026. IEEE.
> [doi:10.1109/QSW72780.2026.00012](https://doi.org/10.1109/QSW72780.2026.00012)

The paper is available at
[ieeexplore.ieee.org/document/11662182](https://ieeexplore.ieee.org/document/11662182).

## BibTeX

If you use `euqalyptus` in academic work, please cite the paper:

```bibtex
@inproceedings{bernheim2026qoalacompiler,
  author    = {Bernheim, Sacha and van der Vecht, Bart and Ferrari, Davide and
               Rivera, Diego and Wehner, Stephanie},
  title     = {A Multi-Level Compiler Pipeline for Qoala Quantum Internet Programs},
  booktitle = {2026 IEEE International Conference on Quantum Software (QSW)},
  year      = {2026},
  month     = jul,
  address   = {Sydney, Australia},
  publisher = {IEEE},
  pages     = {12--24},
  doi       = {10.1109/QSW72780.2026.00012},
  url       = {https://ieeexplore.ieee.org/document/11662182},
}
```

## Where the paper maps onto the code

| Paper topic | Documentation |
| --- | --- |
| The frontend and the pseudo-AST it records | [From Python to Qoala HIR](architecture/python-to-hir.md) |
| Program construction and `compile()` | [SDK reference / Compilation](sdk/compile.md) |
| The branching mechanism | [SDK reference / Branching](sdk/branching.md) |
| Where HIR goes next | [Continuing the pipeline](continuing-pipeline.md) |

## Related repositories

The compiler stack has three leaves, each with its own documentation:

- `euqalyptus` — this project, the Python frontend that emits Qoala HIR.
- [qoala-mlir](https://softwarequtech.github.io/qoala-mlir) — the MLIR-based
  middle and back end that lowers HIR to the executable `.iqoala` format.
- [qoala-bench](https://github.com/SoftwareQuTech/qoala-bench) — the
  benchmarking harness that produced the paper's empirical results. The
  measurements themselves are published as a dataset:
  [doi:10.4121/bcac962c-fa21-40c5-9908-44ea5ccaaa5a.v1](https://doi.org/10.4121/bcac962c-fa21-40c5-9908-44ea5ccaaa5a.v1).
