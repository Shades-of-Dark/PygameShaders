import sys

import pygame

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Image to ASCII")
chars = "...●● "

font = pygame.font.SysFont('consolas', 15)


def text(msg, size=15):
    return font.render(msg, True, (255, 255, 255))


def map_to_range(value, from_x, from_y, to_x, to_y):
    return value * (to_y - to_x) / (from_y - from_x)


def image_to_ascii(image: pygame.Surface):
    image.lock()
    w, h = text("A").get_size()
    surf = pygame.Surface(((image.get_width() - 1) * 15 + w, (image.get_height() - 1) * 15 + h))
    textimgs = {}
    for c in chars:
        textimgs[c] = text(c)

    for j in range(image.get_height()):
        for i in range(image.get_width()):
            r, g, b, _ = image.get_at((i, j))
            grayness = (r + g + b) / 3
            index = round(map_to_range(grayness, 0, 255, 0, len(chars) - 1))
            t = textimgs[chars[index]]
            surf.blit(t, (i * 15, j * 15))

    image.unlock()
    return surf


image = pygame.image.load("michelangelo.jpg").convert()
s = 1/15
image = pygame.transform.scale(image, (1920/15, 1080/15))
pygame.image.save(image_to_ascii(image), "creationofadam.png")
adam = pygame.image.load("creationofadam.png").convert()
while True:
    screen.fill((0, 0, 0))

    screen.blit(adam, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
