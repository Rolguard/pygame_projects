import pygame
import button

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
side_margin = 320
bottom_margin = 80

screen = pygame.display.set_mode((window_width + side_margin, window_height + bottom_margin))
pygame.display.set_caption("Level Editor")

# Define game variables
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

rows = 18
max_cols = 160
# Want tile size to be 48 to match game
tile_size = window_height // rows
tile_types = 38
selected_tile = 0

# Define colours
green = (144, 201, 120)
white = (255, 255, 255)
red = (200, 25, 25)

# Map data (move each level to a .csv file later)
level_data = []

for row in range(rows):
    # Creates a list with -1 repeated max_cols times
    level_r = [-1] * max_cols
    level_data.append(level_r)

# Create ground
for col in range(max_cols):
    level_data[rows - 2][col] = 1
    level_data[rows - 1][col] = 10
print(level_data)


# Loads an image from the given path
def load_image(path, scale, alpha):
    if alpha:
        img = pygame.image.load(f"{path}").convert_alpha()
    else:
        img = pygame.image.load(f"{path}").convert()

    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    return img


# Load images
bg1 = load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-1.png", scale, True)
bg2 = load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-2.png", scale, True)
bg3 = load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-3.png", scale, True)
bg4 = load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-4.png", scale, True)
bg5 = load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-5.png", scale, True)

img_list = []
for i in range(tile_types):
    img = pygame.image.load(f"pygame_images/game1/tiles/{i}.png")
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)
print(len(img_list))

# Make a button list
button_list = []
btn_col = 0
btn_row = 0


# TODO: Make refresh, load and save buttons appear on bottom margin of level editor
for i in range(len(img_list)):
    btn = button.Button(window_width + (btn_col * 70) + 50, btn_row * 70 + 50, img_list[i], 1)
    button_list.append(btn)
    btn_col += 1

    if btn_col == 3:
        btn_col = 0
        btn_row += 1


def draw_bg():
    screen.fill(green)
    width = bg1.get_width()

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
        pygame.draw.line(screen, white, (i * tile_size, 0), (i * tile_size, window_height))

    # Draw horizontal lines up to the rows
    for i in range(rows + 1):
        pygame.draw.line(screen, white, (0, i * tile_size), (window_width, i * tile_size))


def draw_level():
    # row is the individual list, y refers to which row
    for y, row, in enumerate(level_data):
        for x, tile in enumerate(row):
            if tile != -1:
                screen.blit(img_list[tile], (x * tile_size - scroll, y * tile_size))


running = True

while running:
    clock.tick(FPS)
    draw_bg()
    draw_grid()
    draw_level()
    # Draw tile panel and tiles
    pygame.draw.rect(screen, green, (window_width, 0, side_margin, window_height))

    # Button count is incremented with enumerate and used to distinguish buttons from each other
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            # Button class draw method returns a bool that shows whether it has been clicked
            selected_tile = button_count

    pygame.draw.rect(screen, red, (button_list[selected_tile].rect.x, button_list[selected_tile].rect.y,
                                   button_list[selected_tile].rect.size[0], button_list[selected_tile].rect.size[1]), 3)

    # Add new tiles to screen
    pos = pygame.mouse.get_pos()
    level_x = (pos[0] + scroll) // tile_size
    level_y = pos[1] // tile_size

    # Check mouse coordinates are within level grid
    if pos[0] < window_width or pos[1] < window_height:
        # Update tile value
        if pygame.mouse.get_pressed()[0]:
            level_data[level_y][level_x] = selected_tile

        elif pygame.mouse.get_pressed()[2]:
            level_data[level_y][level_x] = -1

    print((level_x, level_y))


    # Scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed

    if scroll_right:
        # As scroll increases, background images move to the left, simulating camera movement to the right
        scroll += 5 * scroll_speed

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

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
