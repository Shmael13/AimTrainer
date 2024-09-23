import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cool thing I made")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)  # Color for SpeedBall

# Game variables
score = 0
health = 3
max_health = 10
combo_count = 0
game_objects = []
trail = []
special_count = 3
speed_multiplier = 0.5
time_elapsed = 0
purple_platform = None
platform_collisions = 0
direction_multiplier = 1
spawn_rate = 0.1

class GameObject:
    def __init__(self, x, y, color, radius):
        global direction_multiplier
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.speed_x = random.uniform(-2, 2) * speed_multiplier * direction_multiplier
        self.speed_y = random.uniform(2, 5) * speed_multiplier
        self.gravity = 0.1 * speed_multiplier
        self.is_sliced = False

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity

    def is_off_screen(self):
        return self.y > HEIGHT + self.radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def check_sliced(self, mouse_pos):
        distance = math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        return distance <= self.radius + 10  # Increased hit area

    def slice(self):
        self.is_sliced = True
        self.color = YELLOW

class Fruit(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN, 20)
        self.points = 1

class SpecialFruit(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, 25)
        self.points = 3

class Bomb(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 20)

class PurpleFruit(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, PURPLE, 75)  # 3 times the size of blue fruit
        self.points = 5

    def slice(self):
        global purple_platform
        super().slice()
        purple_platform = PurplePlatform()

class SpeedBall(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, ORANGE, 15)
        self.points = 2

    def slice(self):
        super().slice()
        shooter.increase_fire_rate()

class PurplePlatform:
    def __init__(self):
        self.width = 200
        self.height = 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 50
        self.speed = 5

    def move(self, direction):
        if direction == 'left':
            self.x = max(0, self.x - self.speed)
        elif direction == 'right':
            self.x = min(WIDTH - self.width, self.x + self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, PURPLE, (self.x, self.y, self.width, self.height))

class Shooter:
    def __init__(self):
        self.width = 20
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2  # Start in the middle of the screen
        self.y = HEIGHT // 2 - self.height // 2
        self.speed = 5
        self.color = BLACK
        self.fire_rate = 1.0  # Shots per second
        self.last_shot_time = 0

    def move(self, dx, dy):
        self.x = max(0, min(WIDTH - self.width, self.x + dx * self.speed))
        self.y = max(0, min(HEIGHT - self.height, self.y + dy * self.speed))

    def shoot(self, current_time):
        if current_time - self.last_shot_time >= 1 / self.fire_rate:
            self.last_shot_time = current_time
            return Ray(self.x + self.width // 2, self.y + self.height // 2)
        return None

    def increase_fire_rate(self):
        self.fire_rate = min(5.0, self.fire_rate + 0.5)  # Cap at 5 shots per second

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

class Ray:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50  # Shortened ray length
        self.height = 5
        self.color = RED
        self.speed = 10

    def move(self):
        self.x += self.speed

    def is_off_screen(self):
        return self.x > WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y - self.height // 2, self.width, self.height))

def spawn_object(current_score):
    global direction_multiplier
    x = random.randint(50, WIDTH - 50)
    y = -20

    bomb_probability = min(0.3, 0.05 + (current_score / 1000) * 0.01)

    if (current_score // 1000) % 2 == 1:
        direction_multiplier = -1
    else:
        direction_multiplier = 1

    if random.random() < 0.1:
        if random.random() < bomb_probability:
            return Bomb(x, y)
        elif random.random() < 0.5:
            return SpecialFruit(x, y)
        elif random.random() < 0.7:
            return PurpleFruit(x, y)
        else:
            return SpeedBall(x, y)
    else:
        return Fruit(x, y)

def use_special():
    global special_count, score, combo_count
    if special_count > 0:
        special_count -= 1
        for obj in game_objects:
            if not isinstance(obj, (SpecialFruit, Bomb)) and not obj.is_sliced:
                obj.slice()
                if isinstance(obj, (Fruit, PurpleFruit, SpeedBall)):
                    score += obj.points
                    combo_count += 1

# Font setup
font = pygame.font.Font(None, 36)

# Main game loop
running = True
clock = pygame.time.Clock()
shooter = Shooter()  # Initialize the shooter
rays = []  # List to store active rays

# Hide the default cursor
pygame.mouse.set_visible(False)

while running:
    dt = clock.tick(60) / 1000.0
    time_elapsed += dt

    spefed_multiplier = 0.2 + (score/30)
    spawn_rate = min(0.2, 0.03 + (score / 60) * 0.01)

    mouse_pos = pygame.mouse.get_pos()
    trail.append(mouse_pos)
    if len(trail) > 10:
        trail.pop(0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (1, 3):
                use_special()

    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
    shooter.move(dx, dy)

    if purple_platform:
        if keys[pygame.K_LEFT]:
            purple_platform.move('left')
        if keys[pygame.K_RIGHT]:
            purple_platform.move('right')

    # Continuous firing
    new_ray = shooter.shoot(pygame.time.get_ticks() / 1000.0)
    if new_ray:
        rays.append(new_ray)

    for obj in game_objects:
        if not obj.is_sliced and obj.check_sliced(mouse_pos):
            obj.slice()
            if isinstance(obj, (Fruit, SpecialFruit, PurpleFruit, SpeedBall)):
                score += obj.points
                combo_count += 1
                if combo_count > 3:
                    score += combo_count
                if isinstance(obj, SpecialFruit):
                    special_count = min(special_count + 1, 3)
                if isinstance(obj, Fruit):
                    health = min(health + 1, max_health)
                if isinstance(obj, SpeedBall):
                    shooter.increase_fire_rate()
            elif isinstance(obj, Bomb):
                health = 0
                combo_count = 0

    if random.random() < spawn_rate:
        game_objects.append(spawn_object(score))

    for obj in game_objects[:]:
        obj.move()
        if obj.is_off_screen():
            game_objects.remove(obj)
            if isinstance(obj, (Fruit, SpecialFruit, PurpleFruit, SpeedBall)) and not obj.is_sliced:
                health -= 1
                combo_count = 0
        elif purple_platform and obj.y + obj.radius > purple_platform.y:
            if purple_platform.x < obj.x < purple_platform.x + purple_platform.width:
                if not obj.is_sliced:
                    obj.speed_y = -abs(obj.speed_y)
                    platform_collisions += 1
                    if platform_collisions >= 10:
                        purple_platform = None
                        platform_collisions = 0

    # Update and check collisions for rays
    for ray in rays[:]:
        ray.move()
        if ray.is_off_screen():
            rays.remove(ray)
        else:
            for obj in game_objects[:]:
                if not obj.is_sliced and ray.x < obj.x < ray.x + ray.width and abs(ray.y - obj.y) < obj.radius:
                    obj.slice()
                    if isinstance(obj, (Fruit, SpecialFruit, PurpleFruit, SpeedBall)):
                        score += obj.points
                        combo_count += 1
                        if isinstance(obj, SpeedBall):
                            shooter.increase_fire_rate()
                    elif isinstance(obj, Bomb):
                        health = 0
                        combo_count = 0

    window.fill(WHITE)

    if len(trail) > 1:
        pygame.draw.lines(window, RED, False, trail, 2)

    for obj in game_objects:
        obj.draw(window)

    for ray in rays:
        ray.draw(window)

    if purple_platform:
        purple_platform.draw(window)

    shooter.draw(window)

    pygame.draw.circle(window, BLACK, mouse_pos, 10, 2)
    pygame.draw.line(window, BLACK, (mouse_pos[0] - 15, mouse_pos[1]), (mouse_pos[0] + 15, mouse_pos[1]), 2)
    pygame.draw.line(window, BLACK, (mouse_pos[0], mouse_pos[1] - 15), (mouse_pos[0], mouse_pos[1] + 15), 2)

    score_text = font.render(f"Score: {score}", True, BLACK)
    health_text = font.render(f"Health: {health}", True, BLACK)
    combo_text = font.render(f"Combo: {combo_count}", True, BLACK)
    special_text = font.render(f"Special: {special_count}", True, BLACK)
    fire_rate_text = font.render(f"Fire Rate: {shooter.fire_rate:.1f}", True, BLACK)
    window.blit(score_text, (10, 10))
    window.blit(health_text, (10, 50))
    window.blit(combo_text, (10, 90))
    window.blit(special_text, (10, 130))
    window.blit(fire_rate_text, (10, 170))

    if health <= 0:
        game_over_text = font.render("Game Over!", True, RED)
        window.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 18))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()

pygame.quit()
