import pygame
from pygame.locals import *
from crt_shader import GraphicEngine

# pygame initialize
pygame.init()
clock = pygame.time.Clock()

screen = pygame.Surface((800, 600)).convert((255, 65282, 16711681, 0))
# you need to give your display OPENGL flag to blit screen using OPENGL
pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

# init shader class
crt_shader = GraphicEngine(screen)
FPS = 60
img = pygame.image.load('textures/img.jpg').convert()
# MAIN LOOP
while True:
    screen.fill((10, 10, 10))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

    # if you want to render a image on display just blit on screen
    screen.blit(img, (pygame.mouse.get_pos()[0] - 250, pygame.mouse.get_pos()[1] - 250))

    # never forget to render your shader
    crt_shader()
    clock.tick(FPS)
