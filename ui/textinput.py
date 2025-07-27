import pygame
import json

class TextInput:
    def __init__(self, font, max_width=None,theme=None,):
        self.text = ""
        self.font = font
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_position = 0
        self.max_width = max_width

        self.backspace_held = False
        self.backspace_timer = 0
        self.BACKSPACE_INITIAL_DELAY = 300
        self.BACKSPACE_REPEAT_INTERVAL = 50
        self.active = True
        self.typing = False
        if theme is not None:
            with open(theme, "r") as f:
                self.theme = json.load(f)

    def handle_event(self, event):
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        self.delete_previous_word()
                    else:
                        self.delete_char()
                    self.backspace_held = True
                    self.backspace_timer = 0
                    self.typing = True
                elif event.key == pygame.K_LEFT:
                    self.cursor_position = max(0, self.cursor_position - 1)
                    self.typing = True
                elif event.key == pygame.K_RIGHT:
                    self.cursor_position = min(len(self.text), self.cursor_position + 1)
                    self.typing = True
                elif event.key == pygame.K_DELETE:
                    self.delete_forward()
                    self.typing = True
                elif event.key == pygame.K_RETURN:
                    self.typing = False
                    return "confirm"

                elif event.key == pygame.K_TAB:
                    self.typing = False
                    return "cancel"

                elif event.unicode and event.unicode.isprintable():
                    self.typing = True
                    self.insert_text(event.unicode)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE:
                    self.backspace_held = False

    def delete_previous_word(self):
        if self.cursor_position == 0:
            return

        i = self.cursor_position

        # Step 1: skip over any spaces or separators
        while i > 0 and i - 1 < len(self.text) and self.text[i - 1] in (' ', '_', '-', '.', '/'):
            i -= 1

        # Step 2: skip over word characters (alphanumerics or other allowed)
        while i > 0 and i - 1 < len(self.text) and (self.text[i - 1].isalnum()):
            i -= 1

        # Slice out the word
        self.text = self.text[:i] + self.text[self.cursor_position:]
        self.cursor_position = i

    def update(self, dt):
        # Cursor blink
        self.cursor_timer += dt
        if self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # Handle backspace hold
        if self.backspace_held:
            self.backspace_timer += dt
            if self.backspace_timer >= self.BACKSPACE_INITIAL_DELAY:
                self.backspace_timer -= self.BACKSPACE_REPEAT_INTERVAL
                self.delete_char()

    def insert_text(self, char):
        self.text = self.text[:self.cursor_position] + char + self.text[self.cursor_position:]
        self.cursor_position += 1

    def delete_char(self):
        if self.cursor_position > 0:
            self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
            self.cursor_position -= 1

    def delete_forward(self):
        if self.cursor_position < len(self.text):
            self.text = self.text[:self.cursor_position] + self.text[self.cursor_position + 1:]

    def draw(self,surf, x, y, width, height, color=(255, 255, 255), box_color=(30, 30, 30)):
        # Draw background box

        pygame.draw.rect(surf, box_color, (x, y, width + 12, height + 8))
        surf.blit(self.font.render(self.text,False,color), (x + 5, y + 4))
        if self.active:
            # Draw cursor
            if self.cursor_visible:
                cursor_x = x + 5 + self.font.size(self.text[:self.cursor_position])[0]
                pygame.draw.line(surf, color, (cursor_x, y + 4), (cursor_x, y + height + 2), 2)

    def get_text(self):
        return self.text
    def set_text(self, text):
        self.text = text
    def reset(self):
        self.text = ""
        self.cursor_position = 0

    def enable(self):
        self.active = True

    def disable(self):
        self.active = False
