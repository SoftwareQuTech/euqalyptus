from qoala.types.classical import ClassicalType


class NoValueError(RuntimeError):
    pass


# Decorator reused from NetQASM repo
def as_int_when_value(cls):
    """A decorator for the `IntegerType` class which makes it behave like an `int`
    when the property `value` is not `None`.
    """

    def wrap_method(method_name):
        """Return a new method for the class given a method name"""
        int_method = getattr(int, method_name)

        def new_method(self, *args, **kwargs):
            """Check if the value is set, otherwise raise an error"""
            value = self.value
            if value is None:
                raise NoValueError(
                    f"The object '{repr(self)}' has no value yet."
                )
            try:
                if isinstance(*args, ClassicalType):
                    raise RuntimeError(
                        "Cannot directly do a binary operation between two. "
                        "Convert them to `int`s first."
                    )
            except TypeError:
                pass
            return int_method(value, *args, **kwargs)

        return new_method

    method_names = [
        "__abs__",
        "__add__",
        "__and__",
        "__bool__",
        "__ceil__",
        "__divmod__",
        "__eq__",
        "__float__",
        "__floor__",
        "__floordiv__",
        "__ge__",
        "__gt__",
        "__hash__",
        "__int__",
        "__invert__",
        "__le__",
        "__lshift__",
        "__lt__",
        "__mod__",
        "__mul__",
        "__ne__",
        "__neg__",
        "__or__",
        "__pos__",
        "__pow__",
        "__radd__",
        "__rand__",
        "__rdivmod__",
        "__rfloordiv__",
        "__rlshift__",
        "__rmod__",
        "__rmul__",
        "__ror__",
        "__round__",
        "__rpow__",
        "__rrshift__",
        "__rshift__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__sub__",
        "__truediv__",
        "__xor__",
        "bit_length",
        "conjugate",
        "denominator",
        "imag",
        "numerator",
        "real",
        "to_bytes",
    ]
    for method_name in method_names:
        setattr(cls, method_name, wrap_method(method_name))
    return cls
