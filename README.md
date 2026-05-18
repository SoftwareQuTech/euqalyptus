# euqalyptus

`euqalyptus` is the Python frontend of the Qoala compiler stack. You write a quantum-network program as a regular Python function or class, call `compile()`, and out comes a Qoala HIR module — the highest-level intermediate representation of the stack, which is then consumed by the [qoala-mlir](<QOALA_MLIR_DOCS_URL>) toolchain for lowering, optimization, and translation to the executable `.iqoala` format.

## Documentation

The full documentation is published at [`<EUQALYPTUS_DOCS_URL>`](<EUQALYPTUS_DOCS_URL>). It covers installation, the SDK reference (programs, compilation, classical and quantum types, qubit operations, remotes, communication, control flow), the worked teleportation example, the frontend's internal architecture, and contributor-facing material.

## Design and paper

For a deeper account of the compiler's design — including how the front-end records SDK calls into a pseudo-AST and emits Qoala HIR, the branching mechanism, and how the front-end fits into the broader compilation pipeline — please refer to the accompanying paper: [`<PAPER_URL>`](<PAPER_URL>).

## Running the documentation locally

You can serve the documentation site locally with the official `squidfunk/mkdocs-material` Docker image, without installing MkDocs into your environment:

```sh
docker run --rm -it -p 8000:8000 -v "$(pwd)":/docs squidfunk/mkdocs-material
```

Run the command from the repository root. The site is then available at <http://localhost:8000>, with live reload on every change to `docs/` or `mkdocs.yml`.

## Citation

If you use `euqalyptus` in academic work, please cite the accompanying paper. A BibTeX entry will be available alongside the paper at the URL above; the placeholder below will be replaced once the paper is published:

```bibtex
<BIBTEX_PLACEHOLDER>
```

## License

`euqalyptus` is released under the MIT License (Copyright © 2025 QuTech). See the [`LICENSE`](LICENSE) file for the full text.
