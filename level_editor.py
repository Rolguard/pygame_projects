import pygame
import button
import csv
import os
import util
import spritesheet

pygame.init()

clock = pygame.time.Clock()
FPS = 60
scale = 4

# Game window, width divisible by 16 and height divisible by 9 (maintain 16:9 aspect ratio)
# height divisible by height of bg image (216) - prevents white lines from going over the bg height
# width and height also divisible by tile_size = 48 [16 x scale (3) in the main game = size of player rect]
# This way player rect is equal to 1 tile
window_width = 1296
window_height = 864
side_margin = 260
bottom_margin = 80

# Create two separate resolutions so that the level editor works for monitors with lower resolution
# Using a lower resolution doesn't mean just changing the size of the screen
# All images pre-loaded with a certain scale need to be readjusted in size

screen = pygame.display.set_mode((window_width + side_margin, window_height + bottom_margin))
pygame.display.set_caption("Level Editor")

determination_font = pygame.font.Font("pygame_images/game1/fonts/DeterminationSansWebRegular-369X.ttf", 32)
# ui_buttons = spritesheet.SpriteSheet(pygame.image.load("pygame_images/button UI.png"))
# new_button = ui_buttons.get_image(8, 4, 16, 16, 1)
#
# pygame.image.save(new_button, "pygame_images/game1/tiles/test_button.png")
# spikes = spritesheet.SpriteSheet(pygame.image.load("pygame_images/game1/spikes/16-bit-spike-Sheet.png"))
# spikes_list = spikes.get_image_list(0, 4, 16, 16, 1, True)
# for idx, img in enumerate(spikes_list):
#     pygame.image.save(img, f"pygame_images/game1/spikes/{idx}.png")

# Define game variables
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
loading_level = False
displaying_error = False

rows = 18
max_cols = 140
# Want tile size to be 48 to match game
tile_size = window_height // rows
tile_types = 39
selected_tile = 0
level = 0

# Define colours
green = (144, 201, 120)
white = (255, 255, 255)
red = (200, 25, 25)
d_pastel_red = (199, 62, 29)
tangerine = (241, 143, 1)

# List containing lists (rows) with integers corresponding to tile type
level_data = []

for row in range(rows):
    # Creates a list with -1 repeated max_cols times
    level_r = [-1] * max_cols
    level_data.append(level_r)

# Create ground for level
for col in range(max_cols):
    level_data[rows - 2][col] = 1
    level_data[rows - 1][col] = 10

default_level_data = level_data


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


# Scale = 4
# Load images, bg = 384x216
bg1 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-1.png", scale, True)
bg2 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-2.png", scale, True)
bg3 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-3.png", scale, True)
bg4 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-4.png", scale, True)
bg5 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-5.png", scale, True)


img_list = []
for i in range(tile_types):
    img = pygame.image.load(f"pygame_images/game1/tiles/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

# Load images after tile types as buttons that have a special purpose
special_btn_imgs = []
tile_dir = "pygame_images/game1/tiles"
num_files = len([name for name in os.listdir(tile_dir) if os.path.isfile(os.path.join(tile_dir, name))])
for i in range(tile_types, num_files):
    img = pygame.image.load(f"pygame_images/game1/tiles/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (tile_size, tile_size))
    special_btn_imgs.append(img)


# Create special buttons
restart_btn = button.Button(808, window_height + 40, 1, special_btn_imgs[0])
load_btn = button.Button(324 * 2, window_height + 40, 1, special_btn_imgs[1])
save_btn = button.Button(808 + 0.5 * 808, window_height + 40, 1, special_btn_imgs[2])
up_level_btn = button.Button(250, window_height + 40, 1, special_btn_imgs[3])
down_level_btn = button.Button(350, window_height + 40, 1, special_btn_imgs[4])
close_btn = button.Button(980, 392, 1, special_btn_imgs[5])

# Make a button list
button_list = []
btn_col = 0
btn_row = 0

for i in range(len(img_list)):
    btn = button.Button(window_width + (btn_col * 70) + 50, btn_row * 70 + 50, 1, img_list[i])
    button_list.append(btn)
    btn_col += 1

    if btn_col == 3:
        btn_col = 0
        btn_row += 1


def draw_bg():
    screen.fill(green)
    width = bg1.get_width()
    # Bg img is repeatedly blit i times across level
    for i in range(4):
        # Different multipliers give parallax background effect
        screen.blit(bg1, ((i * width) - scroll * 0.4, 0))
        screen.blit(bg2, ((i * width) - scroll * 0.5, 0))
        screen.blit(bg3, ((i * width) - scroll * 0.6, 0))
        screen.blit(bg4, ((i * width) - scroll * 0.7, 0))
        screen.blit(bg5, ((i * width) - scroll * 0.8, 0))


def draw_grid():
    # Draw vertical lines up to the maximum columns
    for i in range(max_cols + 1):
        pygame.draw.line(screen, white, (i * tile_size - scroll, 0), (i * tile_size - scroll, window_height))

    # Draw horizontal lines up to the rows
    for i in range(rows + 1):
        pygame.draw.line(screen, white, (0, i * tile_size), (window_width, i * tile_size))


def draw_level():
    # row is the individual list, y refers to which row
    for row_idx, row, in enumerate(level_data):
        for col_idx, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], ((col_idx * tile_size - scroll), row_idx * tile_size))


running = True

while running:
    clock.tick(FPS)
    draw_bg()
    draw_grid()
    draw_level()
    # Draw tile panel and tiles
    pygame.draw.rect(screen, green, (window_width, 0, side_margin, window_height))
    draw_text(f"Level: {level}", determination_font, (255, 255, 255), 50, 884)

    if displaying_error:
        pygame.draw.rect(screen, d_pastel_red, (450, 370, 550, 100))
        draw_text(f"level{level}_data.csv does not exist.", determination_font, tangerine, 500, 400)
        if close_btn.draw(screen) or os.path.exists(f"level{level}_data.csv"):
            displaying_error = False

    if restart_btn.draw(screen):
        level_data = util.load_level("default_level.csv", level_data)

    elif up_level_btn.draw(screen):
        scroll = 0
        try:
            level += 1
            level_data = util.load_level(f"level{level}_data.csv", level_data)
        except FileNotFoundError:
            displaying_error = True

    elif down_level_btn.draw(screen):
        scroll = 0
        try:
            level -= 1
            level_data = util.load_level(f"level{level}_data.csv", level_data)
        except FileNotFoundError:
            displaying_error = True

    elif save_btn.draw(screen):
        # Save current level data
        with open(f"level{level}_data.csv", "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            for row in level_data:
                csv_writer.writerow(row)

    # Button count is incremented with enumerate and used to distinguish buttons from each other
    for button_count, btn in enumerate(button_list):
        if btn.draw(screen):
            selected_tile = button_count

    pygame.draw.rect(screen, red, (button_list[selected_tile].rect.x, button_list[selected_tile].rect.y,
                                   button_list[selected_tile].rect.size[0], button_list[selected_tile].rect.size[1]), 3)
    # Add new tiles to screen
    pos = pygame.mouse.get_pos()
    level_x = (pos[0] + scroll) // tile_size
    level_y = pos[1] // tile_size

    # Check mouse coordinates are within level grid
    if pos[0] < window_width and pos[1] < window_height:
        # Update tile value
        # May need to add check so that the user can only have 1 player tile on the level at all times
        if pygame.mouse.get_pressed()[0]:
            level_data[level_y][level_x] = selected_tile

        elif pygame.mouse.get_pressed()[2]:
            level_data[level_y][level_x] = -1

    # Scroll the map
    if scroll_left and scroll > 0:
        scroll -= 6 * scroll_speed

    if scroll_right and scroll < max_cols * tile_size - window_width:
        # As scroll increases, background images move to the left, simulating camera movement to the right
        scroll += 6 * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            # Change scrolling speed using lshift
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 4
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
