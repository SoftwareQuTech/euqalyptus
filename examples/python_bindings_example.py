from qoalahir.ir import *
from qoalahir.dialects import hir, func


if __name__ == '__main__':
    with Context() as ctx, Location.unknown():
        # We first register the "hir" dialect
        hir.register_dialect(ctx)
        # We need to create a module to start appending thing on
        m = Module.create()
        # And we start inserting things on the body of the module
        with InsertionPoint(m.body):
            # We create the type of the function to append: void -> void
            none_type = NoneType.get(ctx)
            func_type = FunctionType.get(inputs=[none_type], results=[none_type])
            # And we create it with a name and the type
            function = func.FuncOp(
                name="test",
                type=func_type,
            )
            # We create a block at the start of the funciton body
            block = Block.create_at_start(function.body)
            # We insert the rest at the beginning of the created block
            with InsertionPoint(block):
                # Here we create the operations we actually want ot insert
                qubit = hir.NewQubitOp().qout
                op = hir.HadamardOp(qubit)
        # Before closing the context, we print the ASM we just created
        print(m)
