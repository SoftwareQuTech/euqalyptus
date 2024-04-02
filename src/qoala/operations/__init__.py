from qoala.ast.operations.quantum import DeclareRemote


class Remote:
    def __new__(cls, name: str, *args, **kwargs):
        return DeclareRemote(remote_name=name)

    def __init__(self, name: str):
        # Nothing to do here
        pass
