class QuantumProgramNotImplementedError(RuntimeError):

    def __init__(self, name: str, extra_msg: str):
        super().__init__(
            f"Quantum program '{name}' cannot be instantiated. {extra_msg}"
        )


class NotYetCompiledError(RuntimeError):
    pass


class InvalidArgumentError(RuntimeError):
    pass


class NotIntegerArgumentError(InvalidArgumentError):

    def __init__(self, cls_name: str):
        super().__init__(f"'{cls_name}' type only supports integer values")


class NotUnsignedIntegerArgumentError(InvalidArgumentError):

    def __init__(self, cls_name: str):
        super().__init__(f"'{cls_name}' type only supports positive integer values")


class NotFloatArgumentError(InvalidArgumentError):

    def __init__(self, cls_name: str):
        super().__init__(f"'{cls_name}' type only supports positive integer values")


class InvalidArrayArgumentError(InvalidArgumentError):

    def __init__(self, array_base_type: str, native_type: str):
        super().__init__(
            f"Array of type '{array_base_type}' "
            f"can only hold values of type '{native_type}'"
        )


class UnknownRemoteError(RuntimeError):

    def __init__(self, name: str):
        super().__init__(
            f"Unkown remote with name '{name}'. "
            f"Please make sure it was declared using 'Remote'"
        )


class QoalaCompilerError(RuntimeError):
    pass


class UnknownTypeError(QoalaCompilerError):

    def __init__(self, msg: str):
        super().__init__(msg)


class OperandMismatchError(QoalaCompilerError):

    def __init__(self, msg: str):
        super().__init__(msg)


class WrongEvaluationTypeError(QoalaCompilerError):

    def __init__(self, msg: str):
        super().__init__(msg)


class ValueUnknownAtCompileTimeError(QoalaCompilerError):

    def __init__(self, msg: str):
        super().__init__(msg)


class NotYetImplementedError(QoalaCompilerError):

    def __init__(self, msg: str):
        super().__init__(msg)


class OperationNotYetImplementedError(NotYetImplementedError):

    def __init__(self, operation_name: str):
        super().__init__(f"Operation '{operation_name}' has not been implemented yet.")
