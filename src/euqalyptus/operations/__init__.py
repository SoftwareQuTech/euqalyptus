from euqalyptus import QoalaProgram
from euqalyptus.ast.operations.communication import DeclaredRemote


class Remote:
    """Declare a remote node by name.

    ``Remote("Alice")`` registers a symbolic remote-peer alias inside
    the currently-compiling program. Subsequent operations that target
    that peer — :class:`~euqalyptus.types.quantum.Entangle`,
    ``send_int``, ``recv_int``, and so on — refer to the peer by the
    same name. The symbolic name is later resolved by the runtime to a
    concrete numeric node identifier through capability negotiation.

    The constructor is *idempotent*: calling ``Remote("Alice")`` twice
    in the same program returns the same :class:`DeclaredRemote`
    object, so it is safe to call it once per qubit/operation that
    needs the alias, or once at the top of the function.

    Args:
        name: The symbolic name of the remote peer. Must be a Python
            ``str``.

    Returns:
        The :class:`DeclaredRemote` AST node for the named peer — a new
        one on first declaration, the existing one on subsequent calls
        within the same compilation.
    """

    def __new__(cls, name: str, *args, **kwargs):
        remote = QoalaProgram.get_declared_remote(name)
        if remote is not None:
            return remote
        else:
            return DeclaredRemote(remote_name=name)

    def __init__(self, name: str):
        # Nothing to do here
        pass
