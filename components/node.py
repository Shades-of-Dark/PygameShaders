import pygame


class Node():
    _id_counter = 0

    def __init__(self, kind: str, x, y, num_inputs=1):
        self.type = kind
        self.x = x
        self.y = y
        self.width = 130
        self.height = 27
        self.num_inputs = num_inputs

        self.outline_c = (9, 9, 9)
        self.conns = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.out = pygame.Rect(self.x + self.width, self.y + (self.height - 8) // 2, 8, 8)
        self.inp = pygame.Rect(self.x - 12, self.y + (self.height - 6) // 2, 12, 12)

        self.selected = False
        self.connecting = False
        self.touched = False
        self.delete_cons = False

        self.widgets = []

        self.id = Node._id_counter
        Node._id_counter += 1

        self.color = (30, 30, 30)

    def get_next_input_index(self, existing_connections):
        """Get the next available input index for this node"""
        used_indices = {conn.input_index for conn in existing_connections if conn.out == self}

        for i in range(self.num_inputs):
            if i not in used_indices:
                return i

    def update(self, mx, my,minxbound, minybound, xbound, ybound):
        if self.selected:
            xdist = self.x - mx
            ydist = self.y - my
            self.x = pygame.math.clamp(pygame.mouse.get_pos()[0] + xdist,minxbound, xbound)
            self.y = pygame.math.clamp(pygame.mouse.get_pos()[1] + ydist, minybound, ybound)
            self.touched = True

        if self.touched:
            self.outline_c = (230, 75, 61)
        else:
            self.outline_c = (9, 9, 9)

        self.rect.x = self.x
        self.rect.y = self.y
        self.out.x = self.x + self.width
        self.out.y = self.y + (self.height - 8) // 2
        self.inp.x = self.x - 12
        self.inp.y = self.y + (self.height - 6) // 2

    def __eq__(self, other):
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
