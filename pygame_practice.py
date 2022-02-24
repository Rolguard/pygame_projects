import pygame
import os
pygame.init()

window_width = 1280
window_height = 720
screen = pygame.display.set_mode((window_width, window_height))

# Game variables
clock = pygame.time.Clock()
FPS = 60
gravity = 0.8
terminal_velocity = 8

pygame.display.set_caption("Pygame Practice")

# Initialising player
# player_img = pygame.image.load("pygame_images/game1/wizard/Idle/0.png")
# player_img = pygame.transform.scale(player_img, (int(player_img.get_width() * scale),
#                                                  int(player_img.get_height() * scale)))
# player_rect = player_img.get_rect()
# player_rect.center = (200, 200)

moving_left = False
moving_right = False

# Colours
bg_colour = (93, 235, 240)


class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)

        self.char_type = char_type
        self.speed = speed
        # List of sequences of animations (List of lists containing Surfaces)
        self.animation_list = []
        # Action represents which animation folder to use e.g. 0 = Idle animation, 1 = Run animation, 2 = Jump etc.
        self.action = 0
        # frame_index gives which frame of the animation sequence is being played
        self.frame_index = 0
        # Gives the last time in ms the character was updated
        self.update_time = pygame.time.get_ticks()
        self.flip = False
        self.jump = False
        self.in_air = True
        self.velocity_y = 0

        # Load different animation types into self.animation_list
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            temp_list = []
            animation_path = f"pygame_images/game1/{self.char_type}/{animation}"

            if os.path.exists(animation_path):
                # Count the number of frames in the folder
                num_frames = len(os.listdir(animation_path))
                for i in range(num_frames):
                    # Load and scale each frame(file) into a list for animation_list
                    img = pygame.image.load(f"{animation_path}/{i}.png").convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)

            self.animation_list.append(temp_list)

        # Temporary, replace with handling of animations in folders
        # img = pygame.image.load(f"pygame_images/game1/{self.char_type}/Idle/0.png")
        # img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

        self.char_img = self.animation_list[self.action][self.frame_index]
        self.rect = img.get_rect()
        self.rect.center = (x, y)

    def update_animation(self):
        animation_cooldown = 120

        # Update image based on action and frame
        self.char_img = self.animation_list[self.action][self.frame_index]

        # Check if enough time has passed for an animation update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Check if frame_index has reached end of animation sequence
        if self.frame_index >= len(self.animation_list[self.action]):
            # Check for jump animation
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if self.action != new_action:
            self.action = new_action

            # Reset frame and update time such that we begin at the beginning of the animation sequence
            # E.g. Half-way through run animation will transition to beginning of idle animation as soon as you stop
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx -= self.speed
            self.flip = True
        if moving_right:
            dx += self.speed
            self.flip = False

        # Player has input jump command is not in the air
        if self.jump and not self.in_air:
            self.velocity_y -= 28
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.velocity_y += gravity
        if self.velocity_y > terminal_velocity:
            self.velocity_y = terminal_velocity

        dy += self.velocity_y

        # Check if collision will occur with floor
        if self.rect.bottom + dy > 600:
            dy = 600 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        # screen.blit(self.char_img, self.rect.center)
        screen.blit(pygame.transform.flip(self.char_img, self.flip, False), self.rect)


player = Character("wizard", 200, 200, 3, 5)
wraith = Character("wraith", 800, 200, 3, 5)

running = True
while running:
    clock.tick(FPS)
    screen.fill(bg_colour)
    pygame.draw.line(screen, (220, 10, 10), (0, 600), (window_width, 600))

    if player.in_air:
        player.update_action(2)

    elif moving_left or moving_right:
        player.update_action(1)

    else:
        player.update_action(0)

    player.update_animation()
    player.draw()
    wraith.draw()

    player.move(moving_left, moving_right)
    wraith.move(False, False)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP:
                player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False

    pygame.display.update()

pygame.quit()