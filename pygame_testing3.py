import pygame
import sys
from pygame.locals import *

pygame.init()

window_size = (1280, 720)

screen = pygame.display.set_mode(window_size, 0, 32)
pygame.display.set_caption("Jump Knight")
game_icon = pygame.image.load("pygame_images/grass_tile1.png")
pygame.display.set_icon(game_icon)

# For 24x24 sprites probably use 320 x 180, for 32 x 32 sprites use 480 x 270 as base resolution
display = pygame.Surface((640, 360))
clock = pygame.time.Clock()

player_y_momentum = 0
player_model = pygame.image.load("pygame_images/wizard_16x16.png")
dirt_tile = pygame.image.load("pygame_images/dirt_tile_24x24.png")
grass_tile = pygame.image.load("pygame_images/grass_tile_24x24.png")

background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]],
                      [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]],
                      [0.5, [300, 80, 120, 400]]]

player_rect = pygame.Rect(50, 50, player_model.get_width(), player_model.get_height())

moving_right = False
moving_left = False

air_counter = 0


def load_map(path):
    with open(path + ".txt", "r") as f:
        map_data = f.readlines()

    game_map = []

    for row in map_data:
        game_map.append(list(row))

    return game_map


game_map = load_map("map_data")

scroll_movement = [0, 0]

tile_size = grass_tile.get_width()


def collision_test(rect, tiles):
    # We will give player rect and tile_rects as arguments for the collision_test function
    # Hit_list is all tiles which have collided with the player_rect
    hit_list = []

    for hitbox in tiles:
        if rect.colliderect(hitbox):
            hit_list.append(hitbox)

    return hit_list


def move(rect, movement, tiles):
    # Rect is (x location, y location, x pixels wide, y pixels tall)
    # Movement is [x, y], collisions is [a, b, c]
    # Need to measure changes in player position on x-axis
    # After moving player, test for collisions adjust the player's location for any collisions on x-axis
    # Repeat but for y-axis
    # Return rect, collision_types

    # Shows which part of the tile, a collision occurred
    collision_types = {"top": False, "left": False, "bottom": False, "right": False}

    # Handles movement and tests any collisions on the x-axis
    rect.x += movement[0]
    collisions = collision_test(rect, tiles)

    for tile_x in collisions:
        if movement[0] > 0:
            # Player_rect hits the left of the tile
            rect.right = tile_x.left
            collision_types["right"] = True

        if movement[0] < 0:
            # Player_rect hits the right of the tile
            rect.left = tile_x.right
            collision_types["left"] = True

    # Handles movement and tests any collisions on the y-axis
    rect.y += movement[1]
    collisions = collision_test(rect, tiles)

    for tile_y in collisions:
        if movement[1] > 0:
            # Player_rect hits the top of the tile
            rect.bottom = tile_y.top
            collision_types["bottom"] = True

        if movement[1] < 0:
            # Player_rect hits the bottom of the tile
            rect.top = tile_y.bottom
            collision_types["top"] = True

    return rect, collision_types


while True:
    display.fill((144, 200, 255))

    tile_rects = []
    # Setting scroll_movement to adjust at the centre of the player's location
    # E.g. To move the camera to the right, the player and every tile shifts to the left
    # This means scroll_movement[0] is positive, and thus the x of .blit(player_model, (x, y)) and
    # the x of .blit(tile, (x, y)) becomes smaller, shifting the rendering of the player and all tiles to the left

    # If player_rect.x starts at 50 and scroll_movement[0] at 0, 1st loop sm[0] = 50, 2nd = 50
    # If player moves to the right, player_rect.x is increasing by += 3, so 1st sm[0] = 53, 2nd = 53+(56-53)=56 3rd = 59
    # This makes so scroll of x is set to the player's x coordinate
    # We minus scroll_movement[0] by 331 to set camera to start at the centre of the screen of the player on x-axis
    # To do this we take into account the player_model width size and the centre of the non-scaled display on x-axis

    # With the division, adds a fraction of the distance the camera is from the player, adds some lag for smooth camera
    # The closer the camera gets to the player, the lower the scroll_movement, vice-versa for camera further away

    scroll_movement[0] += (player_rect.x - scroll_movement[0] - 331) / 8
    scroll_movement[1] += (player_rect.y - scroll_movement[1] - 191) / 8

    # int_scroll used to prevent pixels on tiles from glitching, moving in place. Original scroll_movement is not int()
    # because we want smaller, decimal numbers for camera smoothness.
    int_scroll = scroll_movement.copy()
    int_scroll[0] = int(scroll_movement[0])
    int_scroll[1] = int(scroll_movement[1])

    # For parallax scrolling where closer objects move faster than objects further away like background which remain
    # almost stationary. Creates a depth effect
    # For every pixel that the camera moves, closer object moves 0.25 with player, further object moves 0.5 with player
    for background_object in background_objects:
        bg_rect = pygame.Rect(background_object[1][0] - scroll_movement[0] * background_object[0],
                              background_object[1][1] - scroll_movement[1] * background_object[0],
                              background_object[1][2], background_object[1][3])

        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), bg_rect)

        else:
            pygame.draw.rect(display, (9, 91, 85), bg_rect)

    # Renders tiles in game_map and puts non-air tiles into tile_rects list for collision testing
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == "1":
                # Put tile on screen, changing to pixel coordinates since tile is 24x24
                display.blit(grass_tile, (x * tile_size - int_scroll[0], y * tile_size - int_scroll[1]))

            if tile == "2":
                display.blit(dirt_tile, (x * tile_size - int_scroll[0], y * tile_size - int_scroll[1]))

            if tile != "0":
                tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))

            x += 1
        y += 1

    # After calling collision_test, returns a list of tiles with the rects that have collied with player_rect
    player_movement = [0, 0]

    if moving_left:
        player_movement[0] -= 3

    if moving_right:
        player_movement[0] += 3

    # Adds gravity to the player, moves 6 pixels down for every 4 frames
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.3

    # Ensures maximum rate of falling (terminal velocity)
    if player_y_momentum > 5:
        player_y_momentum = 5

    player_rect, collision_types = move(player_rect, player_movement, tile_rects)

    if collision_types["bottom"]:
        air_counter = 0
        player_y_momentum = 0

    else:
        # Air_counter is updated each frame
        air_counter += 1

    if collision_types["top"]:
        player_y_momentum = -3
        player_y_momentum = -player_y_momentum

    for event in pygame.event.get():

        # Handles all events with input from the user
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                moving_left = True

            if event.key == K_RIGHT:
                moving_right = True

            if event.key == K_UP:
                # Approx 12 pixels / 8 frames of leeway to jump once falling
                if air_counter <= 8:
                    player_y_momentum = -8

        if event.type == KEYUP:
            if event.key == K_LEFT:
                moving_left = False

            if event.key == K_RIGHT:
                moving_right = False

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    display.blit(player_model, (player_rect.x - scroll_movement[0], player_rect.y - scroll_movement[1]))

    scaled_surface = pygame.transform.scale(display, window_size)
    screen.blit(scaled_surface, (0, 0))

    pygame.display.update()
    clock.tick(60)
