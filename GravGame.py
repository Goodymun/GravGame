import pygame
import sys
from random import randint, weibullvariate
from math import pi, cos, sin
from copy import copy

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
COLOR_STARTPOSITION = (170, 110, 220)
COLOR_BUTTONS = (180, 210, 130)
COLOR_PROJECTILE = (210, 50, 140)
COLOR_TARGET = (170, 220, 40)

# Растры
PLANETS_PICTURES = []
for i in range(1, 22):
	PLANETS_PICTURES.append(pygame.image.load("bods/body" + str(i) + ".png"))

# Константы
PLANET_MAX_DENCITY = 50
MIN_DISTANCE_STARTPOSITION_PLANETS = 50
SPEED_M_NUMBER = 3 #10
GRAVITY_M_NUMBER = 4668.82828 * SPEED_M_NUMBER**-1.98848 #50

# Состояния игры
class GameState:
	TEMP = 'temp'
	GAME_OVER = 'game_over'

# Класс кнопки
class Button:
	def __init__(self, text, x, y, width, height, callback):
		self.text = text
		self.rect = pygame.Rect(x, y, width, height)
		self.callback = callback

	def draw(self, screen):
		pygame.draw.rect(screen, COLOR_BUTTONS, self.rect)
		font = pygame.font.Font(None, 36)
		text_surface = font.render(self.text, True, BLACK)
		screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
								   self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

	def is_clicked(self, pos):
		return self.rect.collidepoint(pos)

# Класс планеты
class Planet:
	def __init__(self, x_planet, y_planet, radius, density):
		self.x_planet = x_planet
		self.y_planet = y_planet
		self.position = (x_planet, y_planet)
		self.radius = radius
		if density > PLANET_MAX_DENCITY:
			self.radius = 2 # Черная дыра
		else:
			self.radius = radius
		self.density = density
		self.color = planet_color_gradient(density)
		self.picture = pygame.transform.scale(PLANETS_PICTURES[randint(0, 20)], (self.radius * 2 + 0, self.radius * 2 + 0))
		self.mass = density * 4 / 3 * pi * radius**3 * .000001
		self.x_mass = x_planet
		self.y_mass = y_planet

	def draw(self, screen):
		pygame.draw.circle(screen, self.color, self.position, self.radius)
		screen.blit(self.picture, (self.x_planet - self.radius, self.y_planet - self.radius))
		pygame.draw.circle(screen, BLACK, self.position, self.radius, 1)
	
	def is_collided(self, x, y, delta):
		return (self.x_planet - x)**2 + (self.y_planet - y)**2 <= (self.radius + delta)**2

def planet_color_gradient(density):
	k = density / PLANET_MAX_DENCITY
	r = round(max(0, 255 * (k - 0.5)))
	g = round(max(0, 255 * (1 - 2 * k)))
	b = 255
	return (min(127, r), g, b)

def planet_density_distribution():
	PLANET_A_DENCITY = 7 # Альфа, масштаб распределения Вейбулла
	PLANET_B_DENCITY = 1.5 # Бета, форма распределения Вейбулла
	if randint(0, 500) == 21: # Вероятность создания черной дыры
		return PLANET_MAX_DENCITY * 1000
	return min(PLANET_MAX_DENCITY, PLANET_A_DENCITY / 2 + weibullvariate(PLANET_A_DENCITY, PLANET_B_DENCITY))

def planets_create(count):
	planets = []
	i = 0
	while i < count:
		searching = True
		while searching:
			radius_planet = randint(10, 100)
			x_planet = randint(radius_planet + 10, WIDTH - 150 - radius_planet - 10)
			y_planet = randint(radius_planet + 10, HEIGHT - radius_planet - 10)
			if not is_collide_planets(planets, x_planet, y_planet, radius_planet * 1.2):
				searching = False
		density_planet = planet_density_distribution()
		planets.append(Planet(x_planet, y_planet, radius_planet, density_planet))
		i += 1
	return planets

def is_collide_planets(planets, x, y, delta):
	for planet in planets:
		if planet.is_collided(x, y, delta):
			return True
	return False

def calculate_acceleration(planets, x, y):
	acceleration_x = 0
	acceleration_y = 0
	for planet in planets:
		delta_x = planet.x_mass - x # проекция расстояния между снярядом и планетой
		delta_y = planet.y_mass - y # проекция расстояния между снярядом и планетой
		if delta_x != 0 and delta_y != 0:
			k = GRAVITY_M_NUMBER / (delta_x**2 + delta_y**2)**1.5  # притягивающий коэффициент
			acceleration_x += delta_x * k * planet.mass
			acceleration_y += delta_y * k * planet.mass
	return (acceleration_x, acceleration_y)

# Класс стартовая позиция
class StartPosition:
	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.position = (x, y)
		self.radius = radius
		self.color = COLOR_STARTPOSITION

	def draw(self, screen):
		pygame.draw.circle(screen, self.color, self.position, self.radius)

def startPosition_create(planets):
	searching = True
	startPosition_radius = 5
	while searching:
		x = randint(startPosition_radius + 10, WIDTH - 150 - startPosition_radius - 10)
		y = randint(startPosition_radius + 10, HEIGHT - startPosition_radius - 10)
		if not is_collide_planets(planets, x, y, startPosition_radius + MIN_DISTANCE_STARTPOSITION_PLANETS):
			searching = False
	return StartPosition(x, y, startPosition_radius)

# Класс снаряд
class ProjectileState:
	MOVING = 'moving'
	WAITING = 'waiting'
	EXPLODING = 'exploding'

class Projectile:
	def __init__(self, state, x, y):
		self.x = x
		self.y = y
		self.position = (x, y)
		self.velocity_x = 0
		self.velocity_y = 0
		#self.velocityAngle = atan2(velocity_x, velocity_y)
		self.acceleration_x = 0
		self.acceleration_y = 0
		self.radius = 3
		self.color = COLOR_PROJECTILE
		self.state = state

	def move(self, planets):
		self.acceleration_x, self.acceleration_y = calculate_acceleration(planets, self.x, self.y)
		self.velocity_x += self.acceleration_x
		self.velocity_y += self.acceleration_y
		self.x += self.velocity_x
		self.y += self.velocity_y
		self.position = (self.x, self.y)
		if is_collide_planets(planets, self.x, self.y, 0):
			self.state = ProjectileState.EXPLODING

	def shoot(self, speed, angle):
		self.velocity_x = speed * cos(angle)
		self.velocity_y = speed * sin(angle)
		self.state = ProjectileState.MOVING

	def draw(self, screen):
		if self.state == ProjectileState.MOVING:
			pygame.draw.circle(screen, self.color, self.position, self.radius)
		elif self.state == ProjectileState.EXPLODING:
			pygame.draw.circle(screen, COLOR_BACKGROUND, self.position, 20)

# Класс траектории
class Trajectory:
	def __init__(self, x_start, y_start, x_velocity, y_velocity):
		self.x_start = x_start
		self.y_start = y_start
		self.x_velocity = x_velocity
		self.y_velocity = y_velocity
		self.coordinates = []
		self.color = COLOR_PROJECTILE

	def draw(self, screen):
		i = 1
		while i < len(self.coordinates):
			if i % 2 == 1:
				pygame.draw.line(screen, self.color, self.coordinates[i - 1], self.coordinates[i])
			i += 1

	def calculate(self, steps_count, planets):
		self.coordinates = []
		phantom_projectile = Projectile(ProjectileState.MOVING, self.x_start, self.y_start)
		i = 0
		while i < steps_count:
			if phantom_projectile.state == ProjectileState.MOVING:
				self.coordinates.append(phantom_projectile.position)
			else:
				break
			phantom_projectile.move(planets)
			i += 1

# Класс цель
class Target:
	def __init__(self, planet, angle):
		self.x_planet = planet.x_planet
		self.y_planet = planet.y_planet
		self.r_planet = planet.radius
		self.x = planet.x_planet + planet.radius * cos(angle)
		self.y = planet.y_planet + planet.radius * sin(angle)
		self.position = (self.x, self.y)
		self.angle = angle
		self.angle_speed = 0
		self.radius = 3
		self.color = COLOR_TARGET

	def move(self):
		if self.angle_speed != 0:
			self.angle += self.angle_speed
			self.angle %= 2 * pi
			self.x = self.x_planet + self.r_planet * cos(self.angle)
			self.y = self.y_planet + self.r_planet * sin(self.angle)
			self.position = (self.x, self.y)

	def draw(self, screen):
		pygame.draw.circle(screen, self.color, self.position, self.radius)

# Главная игра
class Game:
	def __init__(self):
		self.state = GameState.TEMP
		self.buttons = [
			Button("REGEN", 750, 200, 100, 50, self.regen),
			Button("Quit", 750, 300, 100, 50, self.quit_game)
		]
		# self.planets = []
		# self.startPosition = StartPosition(0, 0, 0)
		# self.projectile = Projectile(ProjectilesState.WAITING, 0, 0)
		# self.trajectory = []

	def regen(self):
		self.planets = planets_create(10)
		self.target = Target(self.planets[5], 0)
		self.target.angle_speed = 0.1
		self.startPosition = startPosition_create(self.planets)
		self.projectile = Projectile(ProjectileState.WAITING, self.startPosition.x, self.startPosition.y)
		self.projectile.velocity_x, self.projectile.velocity_y = (10, 0)
		self.trajectory = Trajectory(self.projectile.x, self.projectile.y, self.projectile.velocity_x, self.projectile.velocity_y)
		self.trajectory.calculate(50, self.planets)

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

			if self.state == GameState.TEMP:
				if event.type == pygame.MOUSEBUTTONDOWN:
					for button in self.buttons:
						if button.is_clicked(event.pos):
							button.callback()

			if self.state == GameState.TEMP:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.state = GameState.QUIT
					if event.key == pygame.K_SPACE:
						if self.projectile.state == ProjectileState.WAITING:
							self.projectile.shoot(10, 0)

	def update(self):
		if self.projectile.state == ProjectileState.MOVING:
			self.projectile.move(self.planets)
		elif self.projectile.state == ProjectileState.WAITING:
			self.trajectory.calculate(50, self.planets)
		self.target.move()

	def draw(self):
		SCREEN.fill(COLOR_BACKGROUND)
		for button in self.buttons:
			button.draw(SCREEN)
		if self.projectile.state == ProjectileState.WAITING:
			self.trajectory.draw(SCREEN)
		self.startPosition.draw(SCREEN)
		self.target.draw(SCREEN)
		self.projectile.draw(SCREEN)
		for planet in self.planets:
			planet.draw(SCREEN)
		pygame.display.flip()

	def run(self):
		clock = pygame.time.Clock()
		self.regen()
		while True:
			self.handle_events()
			self.update()
			self.draw()
			clock.tick(30)

if __name__ == "__main__":
	game = Game()
	game.run()
