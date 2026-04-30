# Compilation

Calling `.compile()` on a `QoalaProgram` (or a subclass instance of `QoalaProgramBase`) executes your function under the SDK's recording mode and produces a `QoalaModule` containing Qoala HIR.

## Signature

```python
def compile(
    self,
    *args,
    compile_lazy: bool = False,
    singular_comm_ops: bool = False,
    **kwargs,
) -> tuple[int, QoalaModule]:
    ...
```

`*args` and `**kwargs` are forwarded to the entry function. Returns `(return_value, QoalaModule)`.

![Compilation options](../assets/figures/compile-options.svg)

## Options

### `compile_lazy: bool = False`

When `True`, only build the internal pseudo-AST during `compile()`. The MLIR module is not generated until you explicitly call `.generate_qoala_hir()` on the returned module.

Useful when:

- You want to assert structural properties about the AST in tests without paying the cost of MLIR emission.
- You're debugging the SDK itself.

```python
ret, module = my_program.compile(compile_lazy=True)
# module.asm here would force generation; module is otherwise un-emitted.
```

### `singular_comm_ops: bool = False`

When `True`, classical communication operations emit their **single-value** counterparts in HIR (`qnet.send_int`, `qnet.recv_int`, `qnet.send_float`, `qnet.recv_float`) instead of the tensor-typed multi-value versions (`qnet.send_ints`, `qnet.recv_ints`, …).

Picking this avoids generating tensor values entirely in HIR, which:

- simplifies later passes (no tensor lowering needed),
- matches the standard `unfold-comm-ops` behavior at MIR level (so you'd be doing the work earlier).

```python
_, module = my_program.compile(singular_comm_ops=True)
```

The teleportation example uses this option.

## Class-level toggles

The same flags can be inspected/set on the class for the duration of a session. These methods exist on `QoalaProgram`:

```python
QoalaProgram.compile_lazy_flag(True)
QoalaProgram.compile_singular_comm_ops(True)
```

Call without arguments to read the current value. They are typically only useful in tests or in repeated-compilation harnesses.

## Concurrency

`compile()` is **not** safe to call concurrently from multiple threads on different programs. It uses a global `_compiler_lock` and a class-level `_instance` slot to track the program currently being compiled. The lock makes calls serialize correctly, but the implementation is fundamentally single-threaded.

## Errors

| Exception | Raised when |
| --- | --- |
| `NotYetCompiledError` | You access `.module` on a `QoalaProgram` whose `compile()` has not yet returned successfully. |
| `QuantumProgramNotImplementedError` | A `QoalaProgramBase` subclass is instantiated without an implementation of `main`. |
| `UnknownRemoteError` | `Entangle("X")` is called before `Remote("X")` was declared. |
| `OperandMismatchError`, `NotIntegerArgumentError`, `NotBooleanArgumentError`, etc. | Various semantic checks on operation arguments. See `euqalyptus.errors`. |

## The returned `QoalaModule`

After a successful `compile()` (with `compile_lazy=False`):

| Attribute | Type | Description |
| --- | --- | --- |
| `module.asm` | `str` | Pretty-printed textual Qoala HIR. The canonical input to `qoala-opt`. |
| `module.generic_asm` | `str` | Same module printed in MLIR generic form. |
| `module.functions` | `list[QoalaFunction]` | The functions built during compilation (currently always one). |
| `module.remotes` | `list` | The `DeclaredRemote` objects produced during compilation. |
| `module.current_function` | `QoalaFunction` | The function being built; useful while compiling, generally not afterward. |

`str(module)` is equivalent to `module.asm`. Most pipelines simply do:

```python
print(str(module))
# or:
with open("program.hir.mlir", "w") as f:
    f.write(str(module))
```

…then feed the file to `qoala-opt`. See [Continuing the pipeline](../continuing-pipeline.md).
