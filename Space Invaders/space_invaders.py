import pygame
import os
import time
import random

pygame.font.init()

enemies_left = 5

WIDTH, HEIGHT = 750, 750
ICON = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "icon.png")))
pygame.display.set_icon(ICON)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")


# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_green_small.png")
)
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))


# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Load lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Load background
BG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "background_black.png")), (WIDTH, HEIGHT)
)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        global enemies_left
                        obj.health -= 100
                        if obj.health <= 0:
                            enemies_left -= 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(
            window,
            (255, 0, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width(),
                10,
            ),
        )
        pygame.draw.rect(
            window,
            (0, 255, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 10,
                self.ship_img.get_width() * (self.health / self.max_health),
                10,
            ),
        )


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
    }

    def __init__(self, x, y, color):
        self.color = color
        if self.color == "red":
            self.health = 200
        else:
            self.health = 100
        super().__init__(x, y, self.health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60

    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    lost = False

    enemies = []
    wave_length = 0

    lost_count = 0

    enemy_vel = 2
    player_vel = 5
    player_laser_vel = 5
    enemy_laser_vel = 3

    player = Player(375, 630)

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0, 0))

        # draw text
        global enemies_left
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        enemies_left_label = main_font.render(
            f"Enemies: {enemies_left}", 1, (255, 255, 255)
        )
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(
            enemies_left_label, (WIDTH / 2 - enemies_left_label.get_width() / 2, 10)
        )

        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, HEIGHT / 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            global enemies_left
            level += 1
            wave_length += 5
            enemies_left = wave_length
            player.health = player.max_health
            for i in range(wave_length):
                enemy = Enemy(
                    random.randrange(50, WIDTH - 100),
                    random.randrange(-1500, -100),
                    random.choice(["red", "blue", "green"]),
                )
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0:  # left
            player.x -= player_vel
        if (
            keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH
        ):  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y + player_vel > 0:  # up
            player.y -= player_vel
        if (
            keys[pygame.K_s]
            and player.y + player_vel + player.get_height() + 15 < HEIGHT
        ):  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if enemy.health <= 0:
                enemies.remove(enemy)

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-player_laser_vel, enemies)


def main_menu():
    title_font = pygame.font.Font(os.path.join("assets", "prstart.ttf"), 20)
    description_font = pygame.font.SysFont("comicsans", 15)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(
            "Press mouse button to start game...", 1, (255, 255, 255)
        )

        posY = HEIGHT / 2

        font = pygame.font.SysFont("comicsans", 20)
        text = [
            "Red ships have double health so shoot them twice",
            "WASD to move and spacebar to shoot a laser",
            "If an enemy ship crosses the bottom of the screen, you lose a life",
        ]
        label = []
        for line in text:
            text_label = font.render(line, True, (255, 255, 255))
            label.append(text_label)
        for line in range(len(label)):
            posX = WIDTH / 2 - label[line].get_width() / 2
            posY = HEIGHT / 2 + label[line].get_height()
            position = posX, posY
            WIN.blit(
                label[line],
                (position[0], position[1] + (line * 10) + (15 * line)),
            )

        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
