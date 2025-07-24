from components.node import Node


class Connection():
    def __init__(self, inp: Node, out:Node):
        self.inp = inp
        self.out = out

    def __eq__(self, other):
        return isinstance(other, Connection) and self.inp == other.inp and self.out == other.out

    def __hash__(self):
        return hash((self.inp, self.out))