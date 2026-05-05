from components.node import Node


class Connection():
    def __init__(self, inp: Node, out: Node, input_index=0):
        self.inp = inp  # Input node (receives data)
        self.out = out  # Output node (sends data)
        self.input_index = input_index  # Which input socket (0, 1, 2, etc.)

    def __eq__(self, other):
        return (isinstance(other, Connection) and
                self.inp == other.inp and
                self.out == other.out and
                self.input_index == other.input_index)

    def __hash__(self):
        return hash((self.inp, self.out, self.input_index))