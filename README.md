# Qoala Compiler

This repository contains the implementation of the qoala SDK and qoala compiler frontend.
The implementation is based on the design documents available in the
[qoala-compiler-specs repository](https://gitlab.tudelft.nl/qoala/qoala-compiler-spec)


## Installation

### Requirements

Qoala SDK and compiler has been conceived to work with Python 3.11 or newer. Older versions
are *not* supported.

Additionally, this repository depends on the *qoala-mlir* package, which provides the python
bindings to generate the first intermediate representation of the program. The installation
instructions below will try to retrieve this dependency from an available source, provided
that the python version and architecture is supported.

If no pre-compiled package is available please refer to the [qoala-mlir repository](https://gitlab.tudelft.nl/qoala/qoala-mlir)
to get instructions about how to compile the qoala-mlir package required by this tool.


## SDK Usage

The Qoala SDK provides 2 ways to write a qoala program:

### Inheritance

The SDK provides the `QoalaProgramBase` class in the `qoala` module. A way to write a qoala
program using the inheritance method would be to simply create a new python class *that inherits
from `QoalaProgramBase` and overrides the `main` method:

```python
from qoala import QoalaProgramBase
from qoala.types.classical.integer import Int

class ExampleProgramClass(QoalaProgramBase):
    def main(self):
        int_a = Int(10)
        int_b = Int(20)

        int_c = int_a + int_b
        inc_d = int_b - int_a
        inc_e = int_a * int_a
        inc_f = int_b / int_a
```


### Method decorator

The SDK also provides the `@QoalaProgram` method decorator to write a qoala program. In this way
you can simply add the decorator to any python method to make it a qoala program:

```python
from qoala import QoalaProgram
from qoala.types.classical.integer import Int

@QoalaProgram
def example_program_decorator():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b
    inc_d = int_b - int_a
    inc_e = int_a * int_a
    inc_f = int_b / int_a
```


## Qoala program compilation

After writing a qoala program, it needs to be compiled. This is done by invoking the `compile`
method on the decorated method or an instance of the class that represents the program:

```python
from qoala import QoalaProgram, QoalaProgramBase
from qoala.types.classical.integer import Int

class ExampleProgramClass(QoalaProgramBase):
    def main(self):
        int_a = Int(10)
        int_b = Int(20)

        int_c = int_a + int_b

@QoalaProgram
def example_program_decorator():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b

program_instance = ExampleProgramClass()
ret_a, hir_module_a = compiled_program_class = program_instance.compile()
ret_b, hir_module_b = compiled_program_decorator = example_program_decorator.compile()
```

The `compile` invocation returns 2 things: a return value from the main function of the program
and a *module* object, which is the *Qoala HIR* version of the program.

Since this software contains the *frontend* of the qoala compiler, the program expressed in Qoala
HIR *is still not fully compiled*, and needs to be fed to rest of the compilation pipeline.

To do so, we need to get a textual representation of the Qoala HIR module.

```python
from qoala import QoalaProgram
from qoala.types.classical.integer import Int

@QoalaProgram
def example_program_decorator():
    int_a = Int(10)
    int_b = Int(20)

    int_c = int_a + int_b

_, hir_module = compiled_program_decorator = example_program_decorator.compile()
print(str(hir_module))
# Alternatively we can use print(hir_module.asm) to obtain the same result
```


## Text representation of Qoala HIR module

After getting the Qoala HIR module for the progra, we can easily get a string representation. This
allows us to dump the HIR into a file:



## Continue the compilation

To continue the compilation, we need to make use of the `qoala-opt` and `qoala-translate` tools.
These tools are embedded in the `qoala-mlir` package (part of the dependencies of this package).

To learn more about how to use these 2 extra tools, please refer to the
[qoala-mlir documentation](https://gitlab.tudelft.nl/qoala/qoala-mlir/-/blob/master/README.md?).


# SDK Documentation

## Types

The Qoala SDK exposes some types to use in your programs:
* Classical: Available in the `qoala.types.classical` module: `Int`, `Int32`, `Uint32`, `Bit`,
  `Float`, `Double`, `IntArray` and `FloatArray`.
* Quantum: Available in the `qoala.types.quantum` module: `LocalQubit` and `Entangle`.

Please note that all these types must be used as python objects to correctly instantiate them.
You can also refer to the documentation of the mentioned classes to know more about the types
they represent.


## Operations

Each exposed type also support certain operations that can be invoked ont them:
* Classical fundamental types: These types support the usual `+`, `-`, `*` and `/` operators,
  referring to the addition, substraction, multiplication and division of integers or floats
  respectively. Please note that, currently, operating fundamentals of different types is not
  supported (i.e. no implicit conversion/casting will be made), so trying to do this will
  result in an unspecified behavior.
* Classical arrays: Arrays support the `[]` operator for accessing the members of the declared
  array.
* Quantum entanglement: The `Remote` operation is used to declare a remote before using it
  to entangle qubits.
* Quantum operations: Any declared qubit (local or entangled) can make use of the following
  qubit operations: `X`, `X`, `Z`, `T`, `H`, `K`, `S`, `rot_X`, `rot_Y`, `rot_Z`, `cnot`,
  `cphase`, `cz`, `measure` and `free`.

Please refer to the documentation of each of the operations for more information about them.
