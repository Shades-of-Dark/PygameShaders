import pygame
import json


class PlusButton:
    def __init__(self, x, y, width, height, label, theme=None):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.label = label

        self.clicked = False
        self.active = False  # Set to True when user clicks the button
        self.oneTime = False
        self.oglabel = label
        self.reset = "R"
        self.reset_button = pygame.Rect(self.x - 16, self.y + 2, 12, 12)
        with open(theme, "r") as f:
            self.theme = json.load(f)

    def handle_event(self, events, font):
        mx, my = pygame.mouse.get_pos()

        hovering_reset = self.reset_button.collidepoint(mx, my)
        self.reset = "Reset to Default" if hovering_reset else "R"
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hovering_reset:
                    return "reset_light"

                label_width, _ = font.size(self.label)
                label_x = self.x - label_width - 100
                label_rect = pygame.Rect(label_x, self.y, label_width, self.height)

                if self.active and pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(mx, my):
                    return "add_light"

    def draw_button(self, surf, font, lights):
        # Text sizes
        label_width, _ = font.size(self.label)

        reset_label = "Reset to Default" if self.reset == "Reset to Default" else "R"
        reset_width, reset_height = font.size(reset_label)
        spacing = 8

        # Layout positions
        label_x = self.x - label_width - 5  # Shift label in closer
        label_y = self.y + 2
        button_x = self.x
        button_y = self.y
        reset_x = self.x + self.width + spacing - reset_width / 2
        reset_y = self.y

        # Update reset button rect
        self.reset_button.x = reset_x
        self.reset_button.y = reset_y
        self.reset_button.width = reset_width + 6
        self.reset_button.height = reset_height + 4

        text_c = (255, 255, 255)
        select_c = (255, 0, 0)
        bg_button_c = (60, 60, 60)
        if hasattr(self, "theme"):
            text_c = self.theme["text-color"]
            select_c = self.theme["selected"]
            bg_button_c = self.theme["bg"]
        # Draw label
        surf.blit(font.render(self.label, True, text_c), (label_x, label_y))

        # Draw main button
        color = select_c if self.oneTime else bg_button_c
        pygame.draw.rect(surf, color, pygame.Rect(button_x, button_y, self.width, self.height))
        surf.blit(font.render("+", True, (255, 255, 255)), (button_x, button_y))
        for i in range(1, len(lights) + 1):
            pygame.draw.rect(surf, color, pygame.Rect(button_x, button_y + self.height * i, self.width, self.height))
        # Draw reset button
        pygame.draw.rect(surf, bg_button_c, self.reset_button)
        surf.blit(font.render(reset_label, True, select_c), (self.reset_button.x + 3, self.reset_button.y + 2))

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False
