import pygame


class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    # Returns a new surface specified by width and height that contains a section of the sprite sheet
    def get_image(self, row, frames, width, height, scale, colour=False):

        image = pygame.Surface((width, height)).convert_alpha()
        image.fill((0, 0, 0, 0))
        image.blit(self.sheet, (0, 0), ((frames * width), (row * height), width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))

        if not colour:
            pass
        else:
            # Make background of sprite transparent if bg = colour
            image.set_colorkey(colour)

        return image

    # Returns a list of surfaces from SpriteSheet
    def get_image_list(self, row, num_images, width, height, scale, colour=False):
        image_list = []
        for i in range(num_images):
            image = self.get_image(row, i, width, height, scale, colour)
            image_list.append(image)

        return image_list


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    img = pygame.image.load("pygame_images/game1/Skeleton Sprite Pack/Skeleton/Sprite Sheets/Skeleton Attack.png")
    sprite_sheet = SpriteSheet(img)
    img_list = sprite_sheet.get_image_list(0, 18, 43, 37, 1)
    for idx, frame in enumerate(img_list):
        pygame.image.save(frame, f"pygame_images/game1/skeleton/Attack/{idx}.png")

