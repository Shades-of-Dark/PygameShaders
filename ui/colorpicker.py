import pygame
import json


class ColorPicker():
    def __init__(self, x, y, width, height, label, theme=None, default=(255.0, 255.0, 255.0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.button = pygame.Rect(x, y, width, height)

        with open(theme, "r") as f:
            self.theme = json.load(f)

        self.active = True
        self.oneTime = False
        self.default = default
        self.normal = self.default

        self.image = pygame.image.load("colorwheel.png").convert()
        self.image.set_colorkey((255, 255, 255))
        self.eyedropper = pygame.image.load("eyedropper.png").convert()
        self.eyedropper.set_colorkey((0, 0, 0))

        self.clicked = False

        self.reset = "R"
        self.reset_button = pygame.Rect(self.x, self.y + 2, 12, 12)

        self.boxColor = self.default
        self.color = (self.default[0] / 255, self.default[1] / 255, self.default[2] / 255)

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False

    def draw(self, font, surf):
        # Text sizes
        label_width, _ = font.size(self.label)
        reset_label = "Reset to Default" if self.reset == "Reset to Default" else "R"
        reset_width, reset_height = font.size(reset_label)
        spacing = 8

        # Layout positions
        label_x = self.x - label_width - 5  # Pull label slightly left
        label_y = self.y + 2
        button_x = self.x
        button_y = self.y
        swatch_x = self.x + self.width + spacing
        swatch_y = self.y
        reset_x = swatch_x + self.height + spacing
        reset_y = self.y

        # Update reset button rect
        self.reset_button.x = reset_x - reset_width/2
        self.reset_button.y = reset_y
        self.reset_button.width = reset_width + 6
        self.reset_button.height = reset_height + 4

        # Draw label
        label_c = (255, 255, 255)
        selectColor = (255, 255, 255)
        button_color = (255,255,255)
        text_color = (255, 255, 255)
        if hasattr(self, "theme"):
            label_c = self.theme["text-color"]
            text_color = self.theme["selected"]
            selectColor = self.theme["selected"] if self.oneTime else self.theme["bg"]
            button_color = self.theme["bg"]

        surf.blit(font.render(self.label, True, label_c), (label_x, label_y))

        # Draw main button

        pygame.draw.rect(surf, selectColor, pygame.Rect(button_x, button_y, self.width, self.height))

        # Draw color swatch
        pygame.draw.rect(surf, self.boxColor, pygame.Rect(swatch_x, swatch_y, self.height, self.height))

        # Draw RGB value on top of button
        rgb_text = f"({int(self.normal[0])}, {int(self.normal[1])}, {int(self.normal[2])})"
        rgb_width, _ = font.size(rgb_text)
        surf.blit(font.render(rgb_text, True, label_c),
                  (button_x + self.width / 2 - rgb_width / 2, self.y - 2))

        # Draw reset button
        reset_color = button_color

        pygame.draw.rect(surf, reset_color,
                         pygame.Rect(self.reset_button.x, self.reset_button.y, self.reset_button.width,
                                     self.reset_button.height))
        surf.blit(font.render(reset_label, True, text_color), (self.reset_button.x + 3, self.reset_button.y + 2))

        # Handle eyedropper if active
        if self.oneTime:
            surf.blit(self.image, (self.x, self.y + 20))
            pygame.mouse.set_visible(False)
            mx, my = pygame.mouse.get_pos()
            surf.blit(self.eyedropper, (mx, my))
        else:
            pygame.mouse.set_visible(True)

    def getValue(self):
        return self.color

    def handle_event(self, events, font):
        mx, my = pygame.mouse.get_pos()

        # Hover logic for reset button
        if self.reset_button.collidepoint(mx, my):
            self.reset = "Reset to Default"
        else:
            self.reset = "R"
        if self.active and self.oneTime:
            if self.x + self.image.get_width() > mx >= self.x and self.y + self.image.get_height() > my >= self.y:
                self.boxColor = self.image.get_at((mx - self.x, my - self.y))
        else:
            self.boxColor = self.normal
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_button.collidepoint(mx, my):
                    self.normal = self.default
                    return

                label_width, _ = font.size(self.label)
                label_rect = pygame.Rect(self.x - label_width - 60, self.y, label_width, self.height)
                if label_rect.collidepoint(mx, my):
                    return  # Ignore label clicks

                if self.active and self.oneTime:
                    if self.x + self.image.get_width() >= mx >= self.x and self.y + self.image.get_height() >= my >= self.y:
                        self.normal = self.image.get_at((mx - self.x, my - self.y))
                        self.clicked = True
                        self.oneTime = False
                    else:
                        self.clicked = False
                        self.oneTime = False
                elif self.button.collidepoint(mx, my):
                    self.oneTime = not self.oneTime

        self.color = (self.normal[0] / 255, self.normal[1] / 255, self.normal[2] / 255)
