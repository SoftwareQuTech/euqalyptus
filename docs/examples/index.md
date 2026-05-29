# Examples

The single fully-documented example is the [Teleportation](teleportation/index.md) tutorial, lifted from `examples/teleportation/` in this repo. It is a two-program example: Alice (the sender) prepares a Bell pair with Bob, performs a Bell-state measurement on her side, and sends the two classical correction bits to Bob; Bob (the receiver) applies the corrections and measures.

If you are after more programs, the `tests/bindings/` directory is the best source: it exercises the full Python-to-HIR path with assertions on the emitted module, so each test is effectively a small end-to-end example whose expected output is part of the test fixture.
