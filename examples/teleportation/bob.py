from euqalyptus import QoalaProgram
from euqalyptus.operations import Remote
from euqalyptus.types.quantum import Entangle, ScopedQubit
from euqalyptus.operations.communication import recv_int
from euqalyptus.operations.branching import if_cond
from euqalyptus.operations.control_flow import return_results


@QoalaProgram
def teleport():
    alice = Remote("Alice")
    q_ent = Entangle("Alice")
    x_corr = recv_int(alice)
    z_corr = recv_int(alice)
    with if_cond(z_corr == 1) as (t, f):
        cond_qubit = ScopedQubit(q_ent)
        with t:
            cond_qubit.Z()
            t.yield_value(cond_qubit)
    meas = cond_qubit.measure()
    return_results(meas)


if __name__ == "__main__":
    _, module = teleport.compile(singular_comm_ops=True)
    print(str(module))
