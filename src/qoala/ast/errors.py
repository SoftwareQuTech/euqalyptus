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


class NotYetImplementedError(QoalaCompilerError):
    def __init__(self, msg: str):
        super().__init__(msg)


class OperationNotYetImplementedError(NotYetImplementedError):
    def __init__(self, operation_name: str):
        super().__init__(f"Operation '{operation_name}' has not been implemented yet.")
