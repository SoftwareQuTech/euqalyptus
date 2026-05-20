# euqalyptus

`euqalyptus` is the Python frontend of the Qoala compiler stack. You write a quantum-network program as a regular Python function or class, call `compile()`, and out comes a Qoala HIR module — the highest-level intermediate representation of the stack, which is then consumed by the [qoala-mlir](https://softwarequtech.github.io/qoala-mlir) toolchain for lowering, optimization, and translation to the executable `.iqoala` format.

## Documentation

The full documentation is published at [`https://softwarequtech.github.io/euqalyptus`](https://softwarequtech.github.io/euqalyptus). It covers installation, the SDK reference (programs, compilation, classical and quantum types, qubit operations, remotes, communication, control flow), the worked teleportation example, the frontend's internal architecture, and contributor-facing material.

## Design and paper

For a deeper account of the compiler's design — including how the front-end records SDK calls into a pseudo-AST and emits Qoala HIR, the branching mechanism, and how the front-end fits into the broader compilation pipeline — please refer to the accompanying paper: [`<PAPER_URL>`](<PAPER_URL>).

## Running the documentation locally

You can serve the documentation site locally with the official `squidfunk/mkdocs-material` Docker image, without installing MkDocs into your environment. Because the site uses the `mkdocstrings[python]` plugin to render API documentation from the SDK's docstrings, the command below installs the docs-build dependencies (listed in [`requirements-docs.txt`](requirements-docs.txt)) into the container before serving:

```sh
docker run --rm -it -p 8000:8000 -v "$(pwd)":/docs \
  --entrypoint sh squidfunk/mkdocs-material:latest \
  -c 'pip install --quiet -r requirements-docs.txt && mkdocs serve --dev-addr=0.0.0.0:8000'
```

Run the command from the repository root. The site is then available at <http://localhost:8000>, with live reload on every change to `docs/`, `mkdocs.yml`, or the docstrings under `src/euqalyptus/`.

## Citation

If you use `euqalyptus` in academic work, please cite the accompanying paper. A BibTeX entry will be available alongside the paper at the URL above; the placeholder below will be replaced once the paper is published:

```bibtex
<BIBTEX_PLACEHOLDER>
```

## License

`euqalyptus` is released under the MIT License (Copyright © 2025 QuTech). See the [`LICENSE`](LICENSE) file for the full text.
