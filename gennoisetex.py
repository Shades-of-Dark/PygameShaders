import sys
import noise

import pygame
s = 128
screen = pygame.display.set_mode((s, s))

for y in range(s):
    for x in range(s):
        grey = noise.pnoise2(x * 1.2, y * 1.1)

        grey =  grey * 127.5 + 127.5

        screen.set_at((x, y), (grey, grey, grey))

pygame.image.save(screen, "textures/noisetex.png")
