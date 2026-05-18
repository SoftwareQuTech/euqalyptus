# Programs

A Qoala program is a Python callable annotated such that `euqalyptus` can intercept its body and emit Qoala HIR. There are two equivalent ways to declare one.

![Program models](../assets/figures/program-models.svg)

## `@QoalaProgram` — the decorator

```python
from euqalyptus import QoalaProgram

@QoalaProgram
def my_program():
    ...
```

The decorator wraps your function in an instance with `.compile()` and `.module` accessors. Calling the decorated object is equivalent to calling `.compile()`:

```python
ret_val, module = my_program()           # equivalent to my_program.compile()
ret_val, module = my_program.compile()
```

After a successful compile, `my_program.module` returns the `QoalaModule`. Accessing it before compilation raises `NotYetCompiledError`.

## `QoalaProgramBase` — the class

```python
from euqalyptus import QoalaProgramBase

class MyProgram(QoalaProgramBase):
    def main(self):
        ...
```

You implement `main(self)`, then instantiate and compile:

```python
program = MyProgram()
ret_val, module = program.compile()
```

!!! warning "Quirky `__new__`"
    `QoalaProgramBase.__new__` does some `partial(...)` magic to wire `cls.main` as the entry function. As a result, an instance of a subclass of `QoalaProgramBase` is **not** an instance of `QoalaProgramBase` — it is an instance of `QoalaProgram`. Don't rely on `isinstance(obj, QoalaProgramBase)`.

If `main` is missing or remains `@abstractmethod`, instantiation raises `QuantumProgramNotImplementedError`.

## When to use which

| | Decorator | Class |
| --- | --- | --- |
| Single-shot scripts | ✓ | |
| You need state across compilations | | ✓ |
| Inheritance for a family of related programs | | ✓ |
| You want the program to *also* be callable as a regular function | ✓ (via `compile()`) | |
| Importable in tests as one symbol | both | both |

For most short examples, the decorator is the natural fit. The class form starts to pay off when you have a couple of different programs that share helpers — for instance, the [teleportation example](../examples/teleportation/index.md) is two near-identical programs that could share a base class.

## What the entry function may contain

Inside the body of a `@QoalaProgram` (or a `main` method), the SDK objects don't actually *do* their operation directly — they record an AST node into the active program's module. Conceptually:

```python
@QoalaProgram
def example():
    # Declares a remote symbol; recorded into the AST.
    Remote("Bob")

    # Records a qnet.eprs / qnet.new_qubit op into the current function body.
    q = Entangle("Bob")

    # Records a qnet.measure op; m is a QoalaInteger AST node, not a Python int.
    m = q.measure()
```

This is why operations in qoala programs look like ordinary Python: the SDK is using constructors and methods to build the IR. You can mix in regular Python control structures (loops over compile-time values, helper functions, …) freely — anything that is evaluated before or after the SDK calls is just regular Python. What you cannot do is treat the runtime SDK values (such as `m` above) as plain Python values: comparing `m == 0` returns a *recorded comparison expression*, not a boolean. For control flow that depends on runtime values, see the (currently undocumented) branching operators in `euqalyptus.operations.branching`.

## After compilation

The `QoalaModule` returned from `.compile()` exposes the textual HIR via `module.asm` (the canonical input to `qoala-opt`) and the generic-form variant via `module.generic_asm`. The full list of recorded functions is reachable through `module.functions`, the remote declarations encountered during compilation through `module.remotes`, and the function currently being built (useful for introspection mid-compile, less so afterward) through `module.current_function`. For details on `compile()`'s arguments and what the module exposes, see [Compilation](compile.md).
