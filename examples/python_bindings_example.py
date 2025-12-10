from qnet.ir import *
from qnet.dialects import qnet


if __name__ == "__main__":
    with Context() as ctx, Location.unknown():
        # We first register the "qnet" dialect
        qnet.register_dialect(ctx)
        # We need to create a module to start appending thing on
        m = Module.create()
        # And we start inserting things on the body of the module
        with InsertionPoint(m.body):
            # We create the type of the function to append: void -> void
            func_type = FunctionType.get(inputs=[], results=[])
            # And we create it with a name and the type
            function = qnet.QoalaFunc(
                name="test",
                type=func_type,
            )
            # We create a block at the start of the funciton body
            block = Block.create_at_start(function.body)
            # We insert the rest at the beginning of the created block
            with InsertionPoint(block):
                # Here we create the operations we actually want ot insert
                qubit = qnet.NewQubitOp().qout
                op = qnet.HadamardOp(qubit)
                qnet.QoalaReturn([])
        # Before closing the context, we print the ASM we just created
        print(m)
