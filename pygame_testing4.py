import pygame
import spritesheet
import os
import random

pygame.init()

window_width = 1280
window_height = int((window_width / 16) * 9)

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

# Define font
press_start_font = pygame.font.Font("pygame_images/game1/fonts/PressStart2P-vaV7.ttf", 18)
determination_font = pygame.font.Font("pygame_images/game1/fonts/DeterminationSansWebRegular-369X.ttf", 32)

# Define game variables
gravity = 0.65
terminal_velocity = 9
tile_size = 50

# Defining player action variables
moving_left = False
moving_right = False
shooting = False
lightning = False
# lightning_casted makes sure that lightning can only be casted once per key press
# (player cannot hold button for lightning)
lightning_casted = False


# Loads an image from the given path
def load_image(path, scale, alpha):
    if alpha:
        img = pygame.image.load(f"{path}").convert_alpha()
    else:
        img = pygame.image.load(f"{path}").convert()

    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    return img


# Loads multiple images from files in folder_path into a list
# Images must be numbered from 0, e.g. 0.png, 1.png
def load_image_list(folder_path, scale, num_images):
    images = []
    if os.path.exists(folder_path):
        for i in range(num_images):
            file_path = f"{folder_path}/{i}.png"
            img = load_image(file_path, scale, True)
            images.append(img)

    return images


# Define images
background_img = load_image("pygame_images/21009917.png", 1, False)
lightning_drop_img = load_image("pygame_images/game1/drops/lightning_bolt.png", 2, True)
heart_img1 = load_image("pygame_images/game1/drops/heart1.png", 2, True)
heart_img2 = load_image("pygame_images/game1/drops/heart2.png", 2, True)

# Drops
item_drops = {
    "health": heart_img1,
    "lightning": lightning_drop_img,
    # Can add coins later
}
# Parsing regular images in a folder
wraith_proj_frames = load_image_list("pygame_images/game1/Mini Fires 2/2", 2,
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
    pygame.draw.line(screen, red, (0, 650), (window_width, 650))


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
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # Reset temporary list of images
            temp_list = []
            animation_path = f"pygame_images/game1/{self.char_type}/{animation}"

            if os.path.exists(animation_path):
                # Count number of files in folder
                num_frames = len(os.listdir(animation_path))
                temp_list = load_image_list(animation_path, scale, num_frames).copy()

            # If character does not have an animation_type e.g. "Jump", will append an empty list since path must exist
            # In order for frames to be loaded
            # This will maintain the relationship between number and category
            # E.g. Character has Idle, Run and Death, self.action = 0 - Idle animation, self.action = 1 - Run animation
            # self.action = 3 - Death animation
            self.animation_list.append(temp_list)

        # Access the multiple animation sequences (lists) within animation_list
        # Check if images are actually being loaded
        self.char_img = self.animation_list[self.action][self.frame_index]
        self.pos_float = [x, y]
        self.rect = self.char_img.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        # Update cooldowns
        if self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1

    def move(self, moving_left, moving_right):
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
            # Consider adding feature where the longer the player holds jump, the higher they jump
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

        # Check if collision will occur with floor
        if self.rect.bottom + dy > 650:
            dy = 650 - self.rect.bottom
            self.in_air = False

        # Update rect position using movement variables

        # Need pos_float since pygame.rect will truncate floats e.g. 11 + 1.8 = 12.8 --> 12
        # If you add or subtract floats

        self.pos_float[0] += dx
        self.pos_float[1] += dy
        self.rect.x = self.pos_float[0]
        self.rect.y = self.pos_float[1]

    def shoot(self, proj_frames, proj_group):
        if self.shooting_cooldown == 0:
            if self.char_type == "wraith":
                self.shooting_cooldown = 50
            else:
                self.shooting_cooldown = 15
            # Reminder to lower range of player projectiles - currently just go to end of screen
            proj = Projectile(self.rect.centerx + (1.1 * self.rect.size[0] * self.direction),
                              self.rect.centery, self.direction, proj_frames)
            proj_group.add(proj)

    def ai(self):
        if self.alive and player.alive:
            if not self.idle and random.randint(1, 100) == 1:
                self.idle = True
                self.update_action(0)  # self.action = 0 - idle animation
                self.idle_counter = 60

            # Check if ai can see the player
            if self.vision.colliderect(player.rect):
                # Idle then shoot player
                # print("Wraith sees player")
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
            # Check for jump animation
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            # Check for death animation
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
        # Top middle of rect positioned such that it is half-way between a tile and just above the top of the tile
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
        # self.rect.center = (x, y)

    def update(self):
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

        self.velocity_x = 10
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
        self.rect.x += self.direction * self.velocity_x

        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > window_width:
            # self.kill is method from sprite group class, removes sprite from all groups
            self.kill()

        # Check projectile collision with alive characters
        if pygame.sprite.spritecollide(player, fireball_group, False):
            if player.alive:
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


# Create sprite groups (sprite group = list containing sprites, can call 1 method for all sprites in a group)
fireball_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_drop_group = pygame.sprite.Group()
wraith_proj_group = pygame.sprite.Group()

# Create item_drop
lightning_drop = ItemDrop("lightning", 200, 600)
item_drop_group.add(lightning_drop)

health_drop = ItemDrop("health", 500, 600)
item_drop_group.add(health_drop)

# Create instance of player
# player variable has access to any of the attributes initialised by the constructor
player = Character("wizard", 300, 300, 3, 4, 100, 4)
print(player.char_img.get_width())
# health_bar = HealthBar(10, 10, player.health, player.max_health)

wraith = Character("wraith", 600, 600, 3, 1.7, 50, 0)
wraith2 = Character("wraith", 700, 600, 3, 1.7, 50, 0)
wraith3 = Character("wraith", 580, 600, 3, 1.7, 50, 0)
wraith4 = Character("wraith", 1000, 600, 3, 1.7, 50, 0)
enemy_group.add(wraith)
enemy_group.add(wraith2)
enemy_group.add(wraith3)
enemy_group.add(wraith4)

while running:
    clock.tick(FPS)
    draw_bg()

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
        enemy.ai()
        enemy.update()
        enemy.draw()

    # Update and draw sprite groups
    # Calls update() for all Projectiles (sprites) in the sprite group
    # (Instance of Projectile created when shooting = True)
    fireball_group.update()
    explosion_group.update()
    explosion_group.draw(screen)
    wraith_proj_group.update()
    wraith_proj_group.draw(screen)
    item_drop_group.update()
    item_drop_group.draw(screen)

    if player.alive:
        # Check the state of the player and update player actions
        if shooting:
            # Creates instance of Projectile class and adds to fireball_group (sprite.Group)
            player.shoot(fireball_frames, fireball_group)
            # Need to set up flip for fireballs
        elif lightning and not lightning_casted and player.lightning_charges > 0:
            # Can replace constant (6) with tile_size later, so range of lightning determined by tile length
            lightning_x = player.rect.centerx + (6 * player.rect.size[0] * player.direction)

            # Using -48 (16 x 3) to y because the lightning animation is 32x32 (scale 5), and player is 16x16 (scale 3)
            lightning = Explosion(lightning_x,
                                  player.rect.centery - 48, lightning_frames, "lightning", 2)
            explosion_group.add(lightning)

            # Ensures player will not lose a lightning_charge if casted outside of the screen width
            if not (lightning_x < 0 or lightning_x > window_width):
                player.lightning_charges -= 1
            lightning_casted = True

        if player.in_air:
            player.update_action(2)  # 2: jump
            # Need jump animation to stay on the 5th frame till it reaches the ground
        elif moving_left or moving_right:
            player.update_action(1)  # 1: run
        else:
            player.update_action(0)  # 0: idle
        player.move(moving_left, moving_right)

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
