import pygame
import json

class SelectBox():
    def __init__(self, x, y, width, height, label,choices:[],theme=None, default=True):
        self.dropDown = False
        self.active = True
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.button = pygame.Rect(x, y, width, height)
        self.value = default
        self.choices = choices
        self.choice_rects = [pygame.Rect(x + 2, y + i * 34, width, 30)for i in range(1, len(choices) + 1)]
        if theme is not None:
            with open(theme, "r") as f:
                self.theme = json.load(f)

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def draw(self, surf, font):
        color = (230, 75, 61) if self.dropDown else (31, 31, 31)
        pygame.draw.rect(surf,color, pygame.Rect(self.x, self.y, self.width, self.height))
        surf.blit(font.render(f"{self.label}: {self.value}", False, (255, 255, 255)), (self.x, self.y))

        if self.dropDown:
            i= 0
            for r in self.choice_rects:
                pygame.draw.rect(surf, (65, 65, 67), r)
                surf.blit(font.render(str(self.choices[i]),False,(255, 255, 255)), (r.x, r.y, ))
                i += 1

    def getValue(self):
        return self.value

    def handle_event(self, events):
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if self.active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button.collidepoint(mx, my):
                        self.dropDown = True

                    if self.dropDown:
                        p = 0
                        for rect in self.choice_rects:
                            if rect.collidepoint(mx, my):
                                self.value = self.choices[p]
                                self.dropDown = False
                                break
                            p += 1