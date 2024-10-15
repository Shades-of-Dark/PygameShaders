import pygame
from pygame.locals import *
from crt_shader import Graphic_engine


# pygame initialize
pygame.init()
clock = pygame.time.Clock()

# as usual you will create a display and give it a name
# i named my display as screen
# and you need to give it a Surface to replace old display
screen = pygame.Surface((800, 600)).convert((255, 65282, 16711681, 0))
# you need to give your display OPENGL flag to blit screen using OPENGL
pygame.display.set_mode((800, 600), DOUBLEBUF|OPENGL)

# init shader class
crt_shader =  Graphic_engine(screen)
FPS = 60
img = pygame.image.load('img.jpg').convert()
#MAIN LOOP
while True:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

    # you need to put a image in your folder

    # if you want to render a image on display just blit on screen
    screen.blit(img, pygame.mouse.get_pos())

    # never forget to render your shader
    crt_shader()
    clock.tick(FPS)