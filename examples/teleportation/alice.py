from euqalyptus import QoalaProgram
from euqalyptus.operations import Remote
from euqalyptus.types.quantum import LocalQubit, Entangle
from euqalyptus.operations.communication import send_int, recv_int


@QoalaProgram
def teleport():
    bob = Remote("Bob")
    q_local = LocalQubit()
    q_ent = Entangle("Bob")
    q_local.cnot(q_ent)
    q_local.H()
    m_local = q_local.measure()
    m_ent = q_ent.measure()
    send_int(bob, m_local)
    send_int(bob, m_ent)
    result = recv_int(bob)


if __name__ == "__main__":
    _, module = teleport.compile(singular_comm_ops=True)
    print(str(module))
