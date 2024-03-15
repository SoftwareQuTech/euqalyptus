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
