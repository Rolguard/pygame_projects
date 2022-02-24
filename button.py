import pygame


# Consider using pygame events and MOUSEBUTTONDOWN/UP for handling
# Can add outline to button when being hovered
# Button clicks or any left or right click events

class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.clicked = False
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        # Check mouse position and mouseover conditions
        pos = pygame.mouse.get_pos()  # Returns mouse (x, y) coordinates
        action = False

        if self.rect.collidepoint(pos):
            # Checks if left click is currently being pressed at the time of the call at the button
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        # If left-click is not being held
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action