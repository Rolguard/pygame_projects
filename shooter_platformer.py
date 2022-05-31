import pygame
import spritesheet
import os
import random
import util
import button

pygame.init()

window_width = 1280
window_height = 864

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Scroller")

running = True

# Clock will limit how quickly the game runs, sets framerate
clock = pygame.time.Clock()
FPS = 60

# Define colours
bg_colour = (110, 200, 234)
black = (0, 0, 0)
black2 = (60, 60, 60)
red = (255, 75, 50)
green = (100, 255, 50)
white = (255, 255, 255)
tangerine = (241, 143, 1)

# Define font
press_start_font = pygame.font.Font("pygame_images/game1/fonts/PressStart2P-vaV7.ttf", 18)
determination_font = pygame.font.Font("pygame_images/game1/fonts/DeterminationSansWebRegular-369X.ttf", 32)

# Define game variables
start_game = False
gravity = 0.65
terminal_velocity = 9
level = 0
rows = 18
max_cols = 140

tile_size = window_height // rows
tile_types = 39

# Scroll starts when player moves left or right from centre of screen, assumes player rect size = 1 tile
scroll_start_point = (window_width // 2) - tile_size
# Scrolling of tiles based on velocity of player movement
screen_scroll = 0
# How far scrolled from start screen
bg_scroll = 0


# Defining player action variables
moving_left = False
moving_right = False
shooting = False
lightning = False
# lightning_casted makes sure that lightning can only be casted once per key press
# (player cannot hold button for lightning)
lightning_casted = False

# Define images
bg1 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-1.png", 4, True)
bg2 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-2.png", 4, True)
bg3 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-3.png", 4, True)
bg4 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-4.png", 4, True)
bg5 = util.load_image("pygame_images/game1/Jungle Asset Pack/parallax background/plx-5.png", 4, True)
lightning_drop_img = util.load_image("pygame_images/game1/drops/lightning_bolt.png", 2, True)
heart_img1 = util.load_image("pygame_images/game1/drops/heart1.png", 2, True)
heart_img2 = util.load_image("pygame_images/game1/drops/heart2.png", 2, True)

tile_list = util.load_image_list("pygame_images/game1/tiles", 3, tile_types)
# 1280 x 864
mm_bg1 = util.load_image("pygame_images/game1/parallax_mountain_pack/parallax_mountain_pack/layers/"
                         "parallax-mountain-bg.png", 5, True)

# start_btn_img =

# Drops
item_drops = {
    "health": heart_img1,
    "lightning": lightning_drop_img,
    # Can add coins later
}
# Parsing regular images in a folder
wraith_proj_frames = util.load_image_list("pygame_images/game1/Mini Fires 2/2", 2,
                                          len(os.listdir("pygame_images/game1/Mini Fires 2/2")))

# Parsing sprite sheet
fireball_sprite_sheet = spritesheet.SpriteSheet(pygame.image.load("pygame_images/game1/flames/flame_horizontal.png"))
explosion_sprite_sheet = spritesheet.SpriteSheet(pygame.image.load("pygame_images/game1/flames/flame_explosion.png"))
lightning_sprite_sheet = spritesheet.SpriteSheet(pygame.image.load("pygame_images/game1/lightning/lightning32x32.png"))

fireball_frames = fireball_sprite_sheet.get_image_list(0, 4, 12, 12, 3, black)
fb_explosion_frames = explosion_sprite_sheet.get_image_list(0, 7, 12, 12, 3, black)
lightning_frames = lightning_sprite_sheet.get_image_list(0, 15, 32, 32, 5, black)


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(bg_colour)
    width = bg1.get_width()
    for i in range(4):
        screen.blit(bg1, ((i * width) - bg_scroll * 0.4, 0))
        screen.blit(bg2, ((i * width) - bg_scroll * 0.5, 0))
        screen.blit(bg3, ((i * width) - bg_scroll * 0.6, 0))
        screen.blit(bg4, ((i * width) - bg_scroll * 0.7, 0))
        screen.blit(bg5, ((i * width) - bg_scroll * 0.8, 0))


class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, velocity_x, health, lightning_charges):
        # Blueprint for character creation

        # Inherits functionality from the sprite class in pygame
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.alive = True
        # As of now speed means how many pixels the character will move each iteration
        self.velocity_x = velocity_x
        self.health = health
        self.max_health = health
        self.shooting_cooldown = 0
        self.lightning_charges = lightning_charges
        # direction = 1 means looking right, direction = -1 means looking left
        self.direction = 1
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        # Used to determine when to move to the next frame in the animation sequence
        # .time.get_ticks returns the number of milliseconds since pygame.init() was called
        self.update_time = pygame.time.get_ticks()

        # AI specific variables
        self.move_counter = 0
        self.idle = False
        self.idle_counter = 0
        self.vision = pygame.Rect(0, 0, 300, 30)

        # Load all images for the character
        animation_types = ["Idle", "Run", "Jump", "Death", "Attack"]
        for animation in animation_types:
            # Reset temporary list of images
            temp_list = []
            animation_path = f"pygame_images/game1/{self.char_type}/{animation}"

            if os.path.exists(animation_path):
                # Count number of files in folder
                num_frames = len(os.listdir(animation_path))
                temp_list = util.load_image_list(animation_path, scale, num_frames).copy()

            # If character does not have an animation_type e.g. "Jump", will append an empty list since path must exist
            # In order for frames to be loaded
            # This will maintain the relationship between number and category
            # E.g. Character has Idle, Run and Death, self.action = 0 - Idle animation, self.action = 1 - Run animation
            # self.action = 3 - Death animation
            self.animation_list.append(temp_list)

        # Access the multiple animation sequences (lists) within animation_list
        # Check if images are actually being loaded
        self.char_img = self.animation_list[self.action][self.frame_index]
        # Need pos_float since pygame.rect will truncate floats e.g. 11 + 1.8 = 12.8 --> 12
        # If you add or subtract floats
        self.pos_float = [x, y]
        self.rect = self.char_img.get_rect()
        self.rect.center = (x, y)
        self.width = self.char_img.get_width()
        self.height = self.char_img.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Update cooldowns
        if self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1

    def move(self, moving_left, moving_right):
        scroll = 0
        dx = 0
        dy = 0
        # Assign movement variables if moving_left or moving_right is True
        if moving_left:
            dx = -self.velocity_x
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.velocity_x
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            # TODO: Consider adding feature where the longer the player holds jump, the higher they jump
            # E.g. Short-tap = short jump, Holding = max jump
            # More responsive gameplay
            self.velocity_y = -20
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.velocity_y += gravity
        if self.velocity_y > terminal_velocity:
            self.velocity_y = terminal_velocity

        dy += self.velocity_y

        # Collisions are checked before the character is moved
        for tile in world.obstacle_list:
            # Check if movement will cause collision with tile in the x direction
            if tile[1].colliderect(self.pos_float[0] + dx, self.pos_float[1], self.width, self.height):
                dx = 0

            # Checks if movement will cause collision with tile in the y direction
            if tile[1].colliderect(self.pos_float[0], self.pos_float[1] + dy, self.width, self.height):
                if self.velocity_y < 0:
                    # Character is moving upwards, collides with bottom of rect
                    # Change in y so only character just touch the rect and not any further
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top

                elif self.velocity_y >= 0:
                    # Character is falling down, collides with top of rect
                    self.velocity_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if self.char_type == "wizard":
            if self.rect.left + dx < 0 or self.rect.right + dx > window_width:
                dx = 0
        # Update rect position using movement variables
        # Need pos_float since pygame.rect will truncate floats if you add or subtract floats
        # e.g. 11 + 1.8 = 12.8 --> 12
        # pos_float for precise location of character in decimals

        self.pos_float[0] += dx
        self.pos_float[1] += dy
        self.rect.x = self.pos_float[0]
        self.rect.y = self.pos_float[1]

        # Update scroll based on player position and amount scrolled from starting screen
        if self.char_type == "wizard" and self.alive:
            world_length = world.level_col * tile_size - window_width

            if (self.rect.right > window_width - scroll_start_point and bg_scroll < world_length) \
                    or (self.rect.left < scroll_start_point and bg_scroll > abs(dx)):
                # Must make player still first, then make objects scroll
                self.pos_float[0] -= dx
                self.rect.x = self.pos_float[0]
                scroll = -dx

        return scroll

    def shoot(self, proj_frames, proj_group):
        if self.shooting_cooldown == 0:
            if self.char_type == "wraith":
                self.shooting_cooldown = 50
            else:
                self.shooting_cooldown = 15

            proj = Projectile(self.rect.centerx + (1.1 * self.rect.size[0] * self.direction),
                              self.rect.centery, self.direction, proj_frames)
            proj_group.add(proj)

    def ai(self):
        # TODO: Need to differentiate ai mechanics for wraith and skeleton
        if self.alive and player.alive:
            if not self.idle and random.randint(1, 100) == 1:
                self.idle = True
                self.update_action(0)  # self.action = 0 - idle animation
                self.idle_counter = 60

            # Check if ai can see the player
            if self.vision.colliderect(player.rect):
                # Idle then shoot player
                # print("Wraith sees player")
                if self.char_type == "wraith":
                    self.update_action(0)
                    self.shoot(wraith_proj_frames, wraith_proj_group)
            else:
                if not self.idle:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # self.action = 1 - running animation
                    self.move_counter += 1
                    # Update enemy vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 160 * self.direction, self.rect.centery)

                    if self.move_counter > tile_size:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idle = False

        self.pos_float[0] += screen_scroll
        self.rect.x = self.pos_float[0]

    def update_animation(self):
        # Create timer for next frame in animation
        animation_cooldown = 120

        # Update image depending on current frame
        self.char_img = self.animation_list[self.action][self.frame_index]

        # Check if enough time has passed for another animation update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Reset frame_index if it has reached end of animation sequence
        if self.frame_index >= len(self.animation_list[self.action]):
            # Prevent reset to starting frame for jump animation
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            # Prevent reset to starting frame for death animation
            elif self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1

            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Changes which animation sequence to play if new action is different from previous
        if new_action != self.action:
            self.action = new_action
            # Reset back to start of animation
            # E.g. Half way idle animation, if new action is running, ensures it does not start half way
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.velocity_x = 0
            self.alive = False
            self.update_action(3)

    # Puts character and health_bar on to the screen
    def draw(self):
        # pygame.transform.flip - (img, bool for flip in x axis, bool for flip in y-axis)
        screen.blit(pygame.transform.flip(self.char_img, self.flip, False), self.rect)
        # Can make it so health bar only shows when the enemy character has taken damage
        if self.char_type != "wizard" and self.alive:
            # Draw health backdrop
            pygame.draw.rect(screen, black2, (self.rect.left - 2, self.rect.bottom + 3, self.rect.size[0] + 4, 5 + 4))

            # Draw max_health
            pygame.draw.rect(screen, red, (self.rect.left, self.rect.bottom + 5, self.rect.size[0], 5))
            # Draw current_health
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, green, (self.rect.left, self.rect.bottom + 5, self.rect.size[0] * ratio, 5))


class ItemDrop(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_drops[self.item_type]
        self.rect = self.image.get_rect()
        # midtop means middle of rect's x and top of rect's y
        # Top middle of rect positioned such that it is horizontally half-way between a tile
        # and positioned just above the top of the tile
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        # Check if the player has collided with the drop
        if pygame.sprite.collide_rect(self, player):
            # Player has picked up drop
            if self.item_type == "health":
                player.health += 20
                if player.health > player.max_health:
                    player.health = player.max_health

            elif self.item_type == "lightning":
                player.lightning_charges += 1

            self.kill()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, frames):
        # Inherit methods from pygame's Sprite class and initialise
        pygame.sprite.Sprite.__init__(self)
        # Can adjust such that speed is an argument, so that there can be multiple projectiles with different speeds

        self.velocity_x = 8
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.frames = frames
        self.image = frames[self.frame_index]
        self.flip = False
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Move projectile
        self.rect.x += self.direction * self.velocity_x + screen_scroll

        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > window_width:
            # self.kill is method from sprite group class, removes sprite from all groups
            self.kill()
        # Check for collision with tiles in level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, wraith_proj_group, False):
            player.health -= 5
            self.kill()

        # Check projectile collision for all types of enemies
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, fireball_group, False):
                if enemy.alive:
                    # Create explosion and play explosion animation upon contact of enemy
                    explosion = Explosion(self.rect.centerx, self.rect.centery, fb_explosion_frames, "fireball", 0)
                    explosion_group.add(explosion)
                    enemy.health -= 10
                    self.kill()

        self.update_animation()
        self.draw()

    def update_animation(self):
        animation_cooldown = 120

        # Update image shown based on frame_index
        self.image = self.frames[self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

    def draw(self):
        # Creating my own draw method instead of using draw() in pygame.sprite.Group so I can control flipping of image
        if self.direction < 0:
            self.flip = True

        elif self.direction > 0:
            self.flip = False

        screen.blit((pygame.transform.flip(self.image, self.flip, False)).convert_alpha(), self.rect)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, explosion_type, radius):
        pygame.sprite.Sprite.__init__(self)
        self.explosion_type = explosion_type
        self.radius = radius
        self.frame_index = 0
        self.frames = frames
        self.update_time = pygame.time.get_ticks()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += screen_scroll
        # Update explosion animation
        animation_cooldown = 80

        self.image = self.frames[self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.frames):
            # Reached end of explosion animation
            self.kill()

        # Check and deal damage to any enemies that are in the explosion radius
        # Explosion radius on x-axis and y-axis is based on size of the sprite rect

        for enemy in enemy_group:
            if (abs(self.rect.centerx - enemy.rect.centerx) < tile_size * self.radius
                    and abs(self.rect.centery - enemy.rect.centery) < tile_size * self.radius
                    and self.frame_index == 5):

                if self.explosion_type == "lightning":
                    enemy.health -= 10


class World:
    def __init__(self, level_data):
        self.obstacle_list = []
        self.level_data = level_data
        self.level_col = len(self.level_data[0])

    def process_data(self):
        for row_idx, row in enumerate(self.level_data):
            for col_idx, tile in enumerate(row):
                if tile >= 0:
                    # Tile is not empty
                    img = tile_list[tile]
                    tile_rect = img.get_rect()
                    tile_rect.x = col_idx * tile_size
                    tile_rect.y = row_idx * tile_size

                    tile_data = (img, tile_rect)
                    if tile < 31:
                        self.obstacle_list.append(tile_data)
                    elif tile == 31:
                        # Create skeleton
                        new_skeleton = Character("skeleton", col_idx * tile_size, row_idx * tile_size, 2, 3, 150, 0)
                        enemy_group.add(new_skeleton)
                    elif tile == 32:
                        # Create wraith
                        # If player runs into wraith they die instantly
                        new_wraith = Character("wraith", col_idx * tile_size, row_idx * tile_size, 3, 1.7, 50, 0)
                        enemy_group.add(new_wraith)
                    elif tile == 33:
                        # Create health drops
                        new_health_drop = ItemDrop("health", col_idx * tile_size, row_idx * tile_size)
                        item_drop_group.add(new_health_drop)
                    elif tile == 34:
                        # Create lightning charge drops
                        new_lightning_drop = ItemDrop("lightning", col_idx * tile_size, row_idx * tile_size)
                        item_drop_group.add(new_lightning_drop)
                    elif tile == 35:
                        # Create player
                        new_player = Character("wizard", col_idx * tile_size, row_idx * tile_size, 3, 4, 100, 4)
                    elif tile == 36:
                        # Create spikes
                        spikes = Spikes(img, col_idx * tile_size, row_idx * tile_size)
                        spikes_group.add(spikes)
                    elif tile == 37 or 38:
                        # Decoration (trees)
                        decoration = Decoration(img, col_idx * tile_size, row_idx * tile_size)
                        decoration_group.add(decoration)

        return new_player

    def draw(self):
        # tile[0] = img, tile[1] = tile_rect
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])


class Spikes(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        # Top middle of rect positioned such that it is horizontally half-way between a tile
        # and positioned just above the top of the tile
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (1.2 * tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


# Create sprite groups (sprite group = list containing sprites, can call 1 method for all sprites in a group)
fireball_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_drop_group = pygame.sprite.Group()
wraith_proj_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()

# List containing rows (list) of tiles (-1 = nothing)
level_data = []
for row in range(rows):
    r = [-1] * max_cols
    level_data.append(r)

new_level_data = util.load_level(f'level{level}_data.csv', level_data)
world = World(new_level_data)
player = world.process_data()

# When the game is in and not in main menu, change window resolutions

while running:
    clock.tick(FPS)
    if not start_game:
        # In main menu
        screen.fill(bg_colour)
        screen.blit(mm_bg1, (0, 0))
        draw_text("Start", determination_font, tangerine, window_width // 2, window_height // 2 + 200)
    else:
        draw_bg()
        world.draw()

        # Show player's max health then player's current health
        draw_text("Health: ", determination_font, white, 10, 25)
        for i in range(0, player.max_health, 10):
            screen.blit(heart_img2, (115 + (i * 4), 25))

        for i in range(0, player.health, 10):
            screen.blit(heart_img1, (115 + (i * 4), 25))

        # Show lightning charges
        draw_text("Lightning: ", determination_font, white, 10, 75)
        for i in range(player.lightning_charges):
            screen.blit(lightning_drop_img, (150 + (i * 40), 75))
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.update()
            enemy.ai()
            enemy.draw()

        # Update and draw sprite groups
        # Calls update() for all Projectiles (sprites) in the sprite group
        # (Instance of Projectile created when shooting = True)
        decoration_group.update()
        decoration_group.draw(screen)
        fireball_group.update()
        explosion_group.update()
        explosion_group.draw(screen)
        wraith_proj_group.update()
        wraith_proj_group.draw(screen)
        item_drop_group.update()
        item_drop_group.draw(screen)
        spikes_group.update()
        spikes_group.draw(screen)

        if player.alive:
            # Check the state of the player and update player actions
            if shooting:
                # Creates instance of Projectile class and adds to fireball_group (sprite.Group)
                player.shoot(fireball_frames, fireball_group)
            elif lightning and not lightning_casted and player.lightning_charges > 0:
                lightning_x = player.rect.centerx + (6 * tile_size * player.direction)

                # Using -48 (16 x 3) to y because the lightning animation is 32x32 (scale 5),
                # And player is 16x16 (scale 3)
                lightning = Explosion(lightning_x,
                                      player.rect.centery - 48, lightning_frames, "lightning", 2)
                explosion_group.add(lightning)

                # Ensures player will not lose a lightning_charge if casted outside of the screen width
                if not (lightning_x < 0 or lightning_x > window_width):
                    player.lightning_charges -= 1
                lightning_casted = True

            if player.in_air:
                player.update_action(2)  # 2: jump
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            else:
                player.update_action(0)  # 0: idle

            screen_scroll = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit the game
            running = False

        if event.type == pygame.KEYDOWN:
            # Pressed any key on the keyboard
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
            if event.key == pygame.K_e:
                shooting = True
            if event.key == pygame.K_q:
                lightning = True

            if event.key == pygame.K_ESCAPE:
                # Can change escape to open up main menu later
                running = False

        if event.type == pygame.KEYUP:
            # Released any key on the keyboard
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_e:
                shooting = False
            if event.key == pygame.K_q:
                lightning = False
                lightning_casted = False

    pygame.display.update()

pygame.quit()
