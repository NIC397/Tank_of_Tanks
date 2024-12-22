import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4-Player Tank Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)

# Tank class
class Tank:
    def __init__(self, x, y, color, key, color_name):
        self.x = x
        self.y = y
        self.color = color
        self.color_name = color_name
        self.key = key
        self.angle = 0
        self.spinning = True
        self.spin_direction = 1
        self.bullets = []
        self.hp = 10
        self.destroyed = False
        self.pieces = []
        self.radius = 15
        self.collision_speed = [0, 0]
        self.last_fire_time = 0

    def draw(self):
        if not self.destroyed:
            # Create a surface for the tank (square body)
            tank_surface = pygame.Surface((40, 40), pygame.SRCALPHA)  # Square size 40x40
            tank_surface.fill((0, 0, 0, 0))  # Transparent background
            
            # Draw tank body (square)
            pygame.draw.rect(tank_surface, self.color, (10, 10, 20, 20))  # Square centered in surface
            
            # Draw tank barrel
            pygame.draw.rect(tank_surface, self.color, (30, 15, 7, 10))  # Barrel at the top of the square
            
            # Rotate the entire tank surface
            rotated_tank = pygame.transform.rotate(tank_surface, self.angle)
            
            # Get the rectangle for positioning
            rotated_rect = rotated_tank.get_rect(center=(int(self.x), int(self.y)))
            
            # Blit the rotated tank onto the screen
            screen.blit(rotated_tank, rotated_rect.topleft)

            # Draw HP bar
            bar_width = 30
            bar_height = 5
            pygame.draw.rect(screen, BLACK, (self.x - bar_width//2, self.y - 30, bar_width, bar_height))
            pygame.draw.rect(screen, GREY, (self.x - bar_width//2, self.y - 30, bar_width * (self.hp / 10), bar_height))

        else:
            # Draw destroyed tank pieces
            for piece in self.pieces:
                pygame.draw.circle(screen, self.color, (int(piece[0]), int(piece[1])), 3)

    def update(self):
        if not self.destroyed:
            if self.spinning:
                self.angle += 2 * self.spin_direction
            else:
                self.x += math.cos(math.radians(self.angle))
                self.y -= math.sin(math.radians(self.angle))
            
            # Apply collision speed
            self.x += self.collision_speed[0]
            self.y += self.collision_speed[1]
            
            # Reduce collision speed
            self.collision_speed[0] *= 0.9
            self.collision_speed[1] *= 0.9
            
            # Keep tank within screen bounds
            self.x = max(self.radius, min(self.x, WIDTH - self.radius))
            self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

            # Update bullets
            for bullet in self.bullets:
                bullet.update()
                if (bullet.x - other_tank.x)**2 + (bullet.y - other_tank.y)**2 < other_tank.radius**2:
                    other_tank.take_damage()
                    explosions.append(Explosion(bullet.x, bullet.y, other_tank.color))  # Create an explosion at the hit location
                    tank.bullets.remove(bullet)
                    break
        else:
            for piece in self.pieces:
                piece[0] += piece[2]
                piece[1] += piece[3]
            self.pieces = [p for p in self.pieces if 0 <= p[0] <= WIDTH and 0 <= p[1] <= HEIGHT]

    def fire(self):
        current_time = time.time()
        if not self.spinning and not self.destroyed and current_time - self.last_fire_time >= 0.5:
            bullet_x = self.x + 35 * math.cos(math.radians(self.angle))
            bullet_y = self.y - 35 * math.sin(math.radians(self.angle))
            self.bullets.append(Bullet(bullet_x, bullet_y, self.angle))
            self.last_fire_time = current_time

    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.destroyed = True
            self.create_destruction_pieces()

    def create_destruction_pieces(self):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.pieces.append([self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed])

    def handle_collision(self, other_tank):
        dx = self.x - other_tank.x
        dy = self.y - other_tank.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < self.radius + other_tank.radius:
            angle = math.atan2(dy, dx)
            overlap = (self.radius + other_tank.radius) - distance
            move_x = overlap * math.cos(angle) * 0.5
            move_y = overlap * math.sin(angle) * 0.5
            
            self.collision_speed[0] += move_x
            self.collision_speed[1] += move_y
            other_tank.collision_speed[0] -= move_x
            other_tank.collision_speed[1] -= move_y

    def start_spinning(self):
        if not self.spinning:
            self.spinning = True
            self.spin_direction *= -1  # Reverse spin direction

    def stop_spinning(self):
        self.spinning = False

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 5

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Explosion class
class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 5  # Initial radius of the explosion
        self.max_radius = 20  # Maximum radius of the explosion
        self.active = True

    def update(self):
        if self.radius < self.max_radius:
            self.radius += 1  # Expand the explosion
        else:
            self.active = False  # Mark as inactive when it reaches max size

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 5)  # Draw the explosion outline


# Create tanks
def create_tanks():
    return [
        Tank(100, 100, RED, pygame.K_q, "Red"),
        Tank(WIDTH - 100, 100, GREEN, pygame.K_p, "Green"),
        Tank(100, HEIGHT - 100, BLUE, pygame.K_z, "Blue"),
        Tank(WIDTH - 100, HEIGHT - 100, YELLOW, pygame.K_SLASH, "Yellow")
    ]

tanks = create_tanks()

# Create buttons
rematch_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Play Again", GREEN, WHITE)
quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 110, 200, 50, "Quit", RED, WHITE)

# Draw instructions
def draw_instructions():
    font = pygame.font.Font(None, 24)
    instructions = [
        ("Press and Hold \"Q\" to Fire!", RED, (10, 10)),
        ("Press and Hold \"P\" to Fire!", GREEN, (WIDTH - 200, 10)),
        ("Press and Hold \"Z\" to Fire!", BLUE, (10, HEIGHT - 30)),
        ("Press and Hold \"/\" to Fire!", YELLOW, (WIDTH - 200, HEIGHT - 30))
    ]
    for text, color, pos in instructions:
        rendered_text = font.render(text, True, color)
        screen.blit(rendered_text, pos)

# Game loop
clock = pygame.time.Clock()
running = True
winner = None
explosions = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if winner:
                if rematch_button.is_clicked(event.pos):
                    tanks = create_tanks()
                    winner = None
                elif quit_button.is_clicked(event.pos):
                    running = False

    # Handle key presses
    keys = pygame.key.get_pressed()
    for tank in tanks:
        if not tank.destroyed:
            if keys[tank.key]:
                tank.stop_spinning()
                tank.fire()
            else:
                tank.start_spinning()

    # Update game state
    for tank in tanks:
        tank.update()

    # Check for tank-tank collisions
    for i, tank1 in enumerate(tanks):
        for tank2 in tanks[i+1:]:
            if not tank1.destroyed and not tank2.destroyed:
                tank1.handle_collision(tank2)

    # Check for bullet-tank collisions
    for tank in tanks:
        for other_tank in tanks:
            if tank != other_tank and not other_tank.destroyed:
                for bullet in tank.bullets:
                    if (bullet.x - other_tank.x)**2 + (bullet.y - other_tank.y)**2 < other_tank.radius**2:
                        # Apply damage and remove bullet
                        other_tank.take_damage()
                        explosions.append(Explosion(bullet.x, bullet.y, other_tank.color))  # Create an explosion at the hit location
                        tank.bullets.remove(bullet)
                        break

    # Update and draw explosions
    for explosion in explosions:
        explosion.update()
        if not explosion.active:
            explosions.remove(explosion)  # Remove inactive explosions
            

    # Check for game over
    active_tanks = [tank for tank in tanks if not tank.destroyed]
    if len(active_tanks) == 1 and not winner:
        winner = active_tanks[0]

    # Draw everything
    screen.fill(BLACK)
    for tank in tanks:
        tank.draw()
        for bullet in tank.bullets:
            bullet.draw()

    # Draw explosions after tanks and bullets
    for explosion in explosions:
        explosion.draw()

    if winner:
        font = pygame.font.Font(None, 74)
        text = font.render(f"{winner.color_name} Wins!", True, winner.color)
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 37))
        rematch_button.draw()
        quit_button.draw()

    draw_instructions()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
