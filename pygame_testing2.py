import pygame
import sys
from pygame.locals import *

pygame.init()

window_size = (1280, 720)
window = pygame.display.set_mode(window_size, 0, 32)
display = pygame.Surface((640, 360))

pygame.display.set_caption("Pygame Tester")

game_icon = pygame.image.load("pygame_images/grass_tile1.png")
pygame.display.set_icon(game_icon)
player_model = pygame.image.load("pygame_images/knight_24x24.png")
grass_img = pygame.image.load("pygame_images/grass_tile_24x24.png")
dirt_img = pygame.image.load("pygame_images/dirt_tile_24x24.png")

clock = pygame.time.Clock()

player_location = [100, 100]
player_rect = pygame.Rect(player_location[0], player_location[1], player_model.get_width(), player_model.get_height())

player_y_momentum = 0

moving_left = False
moving_right = False


game_map = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            [2, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0, 1, 1, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
# Air is 0, grass is 1, dirt is 2
y = 0
tile_rects = []

while True:
    display.fill((144, 200, 255))

    # Renders the player image wherever the player's location is
    display.blit(player_model, (player_location[0], player_location[1]))

    # Iterates over the game map, assigning x and y values to each tile so that they can be blited at that position
    for row in game_map:
        x = 0
        for tile in row:
            # Scale x and y coordinates by 24 so that it matches pixel coordinates i.e. images won't overlap
            if tile == 1:
                display.blit(grass_img, (x * 24, y * 24))

            elif tile == 2:
                display.blit(dirt_img, (x * 24, y * 24))

            if tile != 0:
                tile_rects.append(tile)

            x += 1
        y += 1

    # Adds gravity to the player
    player_location[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if moving_left:
        player_location[0] -= 3

    if moving_right:
        player_location[0] += 3

    # Handles all events caused by the player in the game
    for event in pygame.event.get():

        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                moving_left = True

            if event.key == K_RIGHT:
                moving_right = True

        if event.type == KEYUP:
            if event.key == K_LEFT:
                moving_left = False

            if event.key == K_RIGHT:
                moving_right = False

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    scaled_surface = pygame.transform.scale(display, window_size)
    window.blit(scaled_surface, (0, 0))

    pygame.display.update()
    clock.tick(60)
