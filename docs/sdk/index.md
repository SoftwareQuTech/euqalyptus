# SDK reference

The euqalyptus SDK exposes a small set of constructs you can use inside a `@QoalaProgram` body. Pick a topic:

- **[Programs](programs.md)** — `QoalaProgram` decorator, `QoalaProgramBase` class, the two ways to define a program.
- **[Compilation](compile.md)** — `.compile()`, options, the `QoalaModule` it returns.
- **[Classical types](types-classical.md)** — `Int`, `Int32`, `UInt32`, `Bit`, `Float`, `Double`, `IntArray`, `FloatArray`, `Bool`.
- **[Quantum types](types-quantum.md)** — `LocalQubit`, `EntangledQubit`, `ScopedQubit`, `Entangle()`.
- **[Qubit operations](qubit-ops.md)** — every gate, rotation, and the measure/free methods.
- **[Remotes](remotes.md)** — `Remote("Name")`.
- **[Communication](communication.md)** — `send_int`, `recv_int`, etc.
- **[Control flow](control-flow.md)** — `return_results`.

!!! note "Branching is out of scope for now"
    The branching operators (`if_cond`, `if_eq`, `if_lt`, …) exist in `euqalyptus.operations.branching` but are not documented here yet. They remain a known-incomplete area of the codebase and will be covered in a future revision.
