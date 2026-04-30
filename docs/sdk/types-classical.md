# Classical types

Classical values inside a Qoala program are *recorded values* — the SDK's classical types build AST nodes rather than holding plain Python values. From the user's perspective, they behave like the analogous Python types (you can `+`, `-`, `*`, `/` numeric values; you can index arrays), but they emit HIR ops behind the scenes.

Source: `euqalyptus/types/classical/`.

## Numeric types

All numeric types live in `euqalyptus.types.classical`. They share a `NumericOperandsOverload` mixin that overloads `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=`. Comparisons return AST nodes (a recorded comparison op), not Python booleans.

| Class | Width | Signedness | Description |
| --- | ---: | --- | --- |
| `Int32` | 32 | signed | Signed 32-bit integer. |
| `Int` | 32 | signed | Alias for `Int32`. |
| `UInt32` | 32 | unsigned | Unsigned 32-bit integer. |
| `Float` | 32 | — | 32-bit floating-point value. |
| `Double` | 32 | — | Alias for `Float`. (Yes, despite the name.) |
| `Bit` | 1 | unsigned | Single-bit value, typically a measurement outcome. |
| `Bool` | — | — | Boolean. Available under `euqalyptus.types.classical.booleans`. Not re-exported from the package's `__init__`. |

```python
from euqalyptus.types.classical import Int, UInt32, Float

x = Int(10)             # records: %x = qnet integer constant 10
y = Int(20)
z = x + y               # records: %z = qnet add %x, %y
half = Float(0.5)       # records: %half = float constant 0.5
```

!!! warning "Don't mix types in the same expression"
    Operating on instances of *different* fundamental types (e.g. `Int + Float`) is not currently supported and yields unspecified behavior. Convert explicitly via the constructor of the desired target type.

### Constructor patterns

Each numeric type accepts either a Python literal or another value of the same type:

```python
a = Int(10)
b = Int(other=a)        # deep copy of a
```

The `other=` form creates a *new instance* with the same value. Useful when the linearity constraints of HIR require a fresh value for every use site. You can also pass `immediate=` keyword instead of positional.

## Arrays

`euqalyptus.types.classical.arrays` exposes:

| Class | Element type |
| --- | --- |
| `IntArray` | `Int` |
| `FloatArray` | `Float` |

Both inherit from a generic `_Array` and expose:

- `array[i]` — bracket indexing returns the element type.
- `array.store(value)` — append an element. Otherwise arrays are fixed-length.

```python
from euqalyptus.types.classical import IntArray

xs = IntArray(1, 2, 3, 4)
first = xs[0]            # an Int AST node
xs.store(5)              # appends to xs
```

The `length=` keyword can be used to declare a fixed-length empty array:

```python
buf = IntArray(length=10)
```

## `ScopedVar`

`euqalyptus.types.classical.ScopedVar` is the type used by branching constructs that need to "yield" a value out of a conditional block. It's primarily used together with the (currently-undocumented) branching operators. Outside of branching, you won't reach for it directly.

## Constants and immediates

Pass a Python literal to a numeric type's constructor to materialize a runtime constant:

```python
n = Int(0)
ten = Int(10)
total = n + ten          # adds the two recorded values
```

Comparisons against immediates are also recorded:

```python
m = qubit.measure()     # m is a Bit
is_one = m == 1          # recorded equality op, not a Python bool
```

This is how the branching operators end up with rich predicate expressions even though the user wrote them as ordinary Python.
