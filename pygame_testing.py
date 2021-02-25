import pygame
import sys
from pygame.locals import *

pygame.init()

window_size = (1280, 720)
screen = pygame.display.set_mode(window_size, 0, 32)
clock = pygame.time.Clock()

display = pygame.Surface((600, 400))

player_model = pygame.image.load("pygame_images/knight_1.png")
grass_image = pygame.image.load("pygame_images/grass_tile1.png")
dirt_image = pygame.image.load("pygame_images/dirt_tile1.png")

player_rect = pygame.Rect(50, 50, player_model.get_width(), player_model.get_height())

moving_left = False
moving_right = False
moving_up = False
moving_down = False

player_y_velocity = 0
air_timer = 0

# Currently issue where the tiles are not being displayed

game_map = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
            [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

# 0 is air, 2 is grass, 1 is dirt


def collision_test(rect, tiles):
    hit_list = []

    for hitbox in tiles:
        if rect.colliderect(hitbox):
            hit_list.append(hitbox)

    return hit_list


def move(rect, movement, tiles):
    # Movement is (x, y)
    collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False}

    # Rect is the rectangle colliding with the tile, which moves based on the x value of movement
    rect.x += movement[0]

    collisions = collision_test(rect, tiles)

    for tile_x in collisions:
        if movement[0] > 0:
            # If the rect is going right, adjust the x position so that the right side of the rect = left side of tile
            rect.right = tile_x.left
            collision_types['right'] = True

        elif movement[0] < 0:
            rect.left = tile_x.right
            collision_types['left'] = True

    rect.y += movement[1]
    collisions = collision_test(rect, tiles)

    for tile_y in collisions:

        if movement[1] > 0:
            # The bottom of the player_rect is colliding with the top of the tile, stops player from falling through
            rect.bottom = tile_y.top
            collision_types['bottom'] = True

        elif movement[1] < 0:
            rect.top = tile_y.bottom
            collision_types['top'] = True

    # Returns the rect's new position to adjust for the collision and gives the type of collision that occurred
    return rect, collision_types


while True:

    display.fill((144, 246, 255))

    # Tile is 32 x 32 pixels
    tile_size = grass_image.get_width()

    tile_rects = []

    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == 1:
                # Need to multiply by 32 to get pixel coordinates, meaning coordinates will account for the image size
                display.blit(dirt_image, (x * tile_size, y * tile_size))

            if tile == 2:
                display.blit(grass_image, (x * tile_size, y * tile_size))

            if tile != 0:
                # Outlines all possible tiles that can be collided with
                tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))

            x += 1
        y += 1

    # This is not the position of the player, its his velocity
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2

    if moving_left:
        player_movement[0] -= 2


    # Enables gravity for the player
    player_movement[1] += player_y_velocity
    # Player moves 4.5 pixels in 5 frames
    player_y_velocity += 0.3

    if player_y_velocity > 5:
        player_y_velocity = 5

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_y_velocity = 0
        air_timer = 0

    else:
        air_timer += 1

    if collisions['top']:
        player_y_velocity = -player_y_velocity

    display.blit(player_model, (player_rect.x, player_rect.y))

    scaled_surface = pygame.transform.scale(display, window_size)
    screen.blit(scaled_surface, (0, 0))

    # Handles all events from the player in pygame
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                moving_left = True

            if event.key == K_RIGHT:
                moving_right = True

            if event.key == K_UP:
                if air_timer <= 8:
                    player_y_velocity = -8

        if event.type == KEYUP:
            if event.key == K_LEFT:
                moving_left = False

            if event.key == K_RIGHT:
                moving_right = False

            if event.key == K_UP:
                moving_up = False

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    clock.tick(60)
