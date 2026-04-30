# Examples

Each example is a complete, runnable Qoala program (or pair of programs) lifted from the `examples/` directory of this repo, plus a short walkthrough.

- **[Teleportation](teleportation/index.md)** — Alice (the sender) prepares a Bell pair with Bob, performs a Bell-state measurement on her side, and sends the two classical correction bits to Bob. Bob (the receiver) applies the corrections and measures.

If you're after more programs, browse:

- `examples/` in this repo (`teleport.py`, `example.py`, `ghz.py`, `classical.py`, `entanglement.py`, …) — runnable scripts.
- `tests/bindings/` — exercises the full Python → HIR path with assertions on the emitted module.
