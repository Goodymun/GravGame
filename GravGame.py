import pygame
import os
import sys
from random import randint, weibullvariate
from math import pi, cos, sin, atan2

# Инициализация Pygame
pygame.init()

# Параметры экрана
WIDTH, HEIGHT = 900, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GravGame")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
COLOR_BACKGROUND = (30, 30, 30)
COLOR_PLANET = (60, 120, 180)
COLOR_STARTPOSITION = (169, 110, 220)
COLOR_BUTTONS = (180, 210, 130)

# Растры
PLANETS_PICTURES = []
image_dir = "bods/"
for image_file in os.listdir(image_dir):
    image_path = os.path.join(image_dir, image_file)
    image = pygame.image.load(image_path)
    PLANETS_PICTURES.append(image)


# Константы
PLANET_MAX_DENCITY = 50


# Состояния игры
class GameState:
    MENU = 'menu'
    PLAY = 'play'
    GAME_OVER = 'game_over'


# Класс кнопки
class Button:
    def __init__(
            self, text: str,
            x: int,
            y: int,
            width: int,
            height: int,
            callback: callable
            ):
        """
        Создание новой кнопки.

        :param text: Текст отображаемы на кнопке.
        :param x: Координата x для левого-верхнего угла кнопки.
        :param y: Координата y для левого-верхнего угла кнопки.
        :param width: Ширина кнопки.
        :param height: Высота кнопки.
        :param callback: Вызываемая функция при нажатии на кнопку.
        """
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_BUTTONS, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, BLACK)
        screen.blit(
            text_surface,
            (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
             self.rect.y + (self.rect.height - text_surface.get_height()) // 2)
             )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Класс планеты
class Planet:
    def __init__(
            self, x_planet: int,
            y_planet: int,
            radius: int,
            density: int
            ):
        """
        Создание новой планеты.

        :param x_planet: Координата x для центра планеты.
        :param y_planet: Координата y для центра планеты.
        :param radius: Радиус планеты.
        :param density: Средняя плотность пород планеты.
        """
        self.x_planet = x_planet
        self.y_planet = y_planet
        self.position = (x_planet, y_planet)
        self.radius = radius
        if density > PLANET_MAX_DENCITY:
            self.radius = 2  # Черная дыра
        else:
            self.radius = radius
        # self.density = density
        self.color = planet_color_gradient(density)
        self.picture = pygame.transform.scale(
            PLANETS_PICTURES[randint(0, 20)],
            (self.radius * 2 + 0, self.radius * 2 + 0)
            )
        self.mass = density * 4 / 3 * pi * radius**3 * .000001
        self.x_mass = x_planet
        self.y_mass = y_planet

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        screen.blit(self.picture, (
            self.x_planet - self.radius, self.y_planet - self.radius
            ))
        pygame.draw.circle(screen, BLACK, self.position, self.radius, 1)

    def is_collided(self, x, y, delta):
        return (
            (self.x_planet - x)**2 +
            (self.y_planet - y)**2 <=
            (self.radius + delta)**2
            )


class Projectile:
    def __init__(
            self, x_projectile: int,
            y_projectile: int,
            radius: int,
            density: int,
            # speed: int
            velocity_x: int,
            velocity_y: int
            ):
        """
        Создание снаряда.

        :param x_projectile: Координата x для центра снаряда.
        :param y_projectile: Координата y для центра снаряда.
        :param radius: Радиус снаряда.
        :param density: Плотность снаряда.
        """
        self.x_projectile = x_projectile
        self.y_projectile = y_projectile
        self.position = (x_projectile, y_projectile)
        self.radius = radius
        self.density = density
        self.color = COLOR_STARTPOSITION
        self.mass = density * 4 / 3 * pi * radius**3 * .000001
        # self.speed = speed
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self):
        self.x_projectile += self.velocity_x
        self.y_projectile += self.velocity_y
        self.position = (self.x_projectile, self.y_projectile)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)


def planet_color_gradient(density):
    k = density / PLANET_MAX_DENCITY
    r = round(max(0, 255 * (k - 0.5)))
    g = round(max(0, 255 * (1 - 2 * k)))
    b = 255
    return (min(127, r), g, b)


def planet_density_distribution():
    PLANET_A_DENCITY = 7  # Альфа, масштаб распределения Вейбулла
    PLANET_B_DENCITY = 1.5  # Бета, форма распределения Вейбулла
    if randint(0, 500) == 21:  # Вероятность создания черной дыры
        return PLANET_MAX_DENCITY * 1000
    return min(
        PLANET_MAX_DENCITY, PLANET_A_DENCITY / 2 +
        weibullvariate(PLANET_A_DENCITY, PLANET_B_DENCITY)
        )


def planets_create(count):
    planets = []
    i = 0
    while i < count:
        searching = True
        while searching:
            radius_planet = randint(10, 100)
            x_planet = randint(
                radius_planet + 10, WIDTH - 200 - radius_planet - 10
                )
            y_planet = randint(radius_planet + 10, HEIGHT - radius_planet - 10)
            if not is_collide_planets(planets,
                                      x_planet, y_planet,
                                      radius_planet * 1.2):
                searching = False
        density_planet = planet_density_distribution()
        planets.append(Planet(x_planet,
                              y_planet,
                              radius_planet,
                              density_planet))
        i += 1
    return planets


def is_collide_planets(planets, x, y, delta):
    for planet in planets:
        if planet.is_collided(x, y, delta):
            return True
    return False


# Главная игра
class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.buttons_menu = [
            Button("Start game", 375, 200, 150, 50, self.start_game),
            Button("Quit", 410, 300, 80, 50, self.quit_game)
        ]
        self.buttons_play = [
            Button("Regen space", 710, 200, 170, 50, self.regen),
            Button("Quit", 710, 300, 170, 50, self.quit_game),

        ]
        self.planets = []
        self.projectiles = []

    def start_game(self):
        self.state = GameState.PLAY
        self.regen()

    def regen(self):
        self.planets = planets_create(20)
        self.projectiles = []

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def game_over(self):
        self.state = GameState.GAME_OVER

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == GameState.PLAY:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    all_battons = self.buttons_play
                    if not any(
                        button.is_clicked(event.pos) for button in all_battons
                    ):
                        self.shoot(event.pos)
                    for button in self.buttons_play:
                        if button.is_clicked(event.pos):
                            button.callback()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.QUIT

            if self.state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons_menu:
                        if button.is_clicked(event.pos):
                            button.callback()

    def shoot(self, target_position):
        start_position = (0, 0)
        angle = atan2(
            target_position[1] - start_position[1],
            target_position[0] - start_position[0]
            )
        speed = 5
        velocity_x = cos(angle) * speed
        velocity_y = sin(angle) * speed
        projectile = Projectile(
            x_projectile=start_position[0],
            y_projectile=start_position[1],
            radius=5,
            density=10,
            velocity_x=velocity_x,
            velocity_y=velocity_y
        )
        self.projectiles.append(projectile)

    def update(self):
        for projectile in self.projectiles:
            projectile.update()

    def draw(self):
        SCREEN.fill(COLOR_BACKGROUND)

        for planet in self.planets:
            planet.draw(SCREEN)

        for projectile in self.projectiles:
            projectile.draw(SCREEN)

        for batton in self.buttons_play:
            batton.draw(SCREEN)

        pygame.display.flip()

    def screen_menu(self):
        SCREEN.fill(COLOR_BACKGROUND)

        for batton in self.buttons_menu:
            batton.draw(SCREEN)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        # self.regen()
        while True:
            self.handle_events()
            self.update()
            if self.state == GameState.MENU:
                self.screen_menu()
            elif self.state == GameState.PLAY:
                self.draw()
            clock.tick(30)


if __name__ == "__main__":
    game = Game()
    game.run()
