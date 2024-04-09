from qoala import QoalaProgram
from qoala.ast.operations.quantum import DeclaredRemote


class Remote:
    def __new__(cls, name: str, *args, **kwargs):
        remote = QoalaProgram.get_declared_remote(name)
        if remote is not None:
            return remote
        else:
            return DeclaredRemote(remote_name=name)

    def __init__(self, name: str):
        # Nothing to do here
        pass
