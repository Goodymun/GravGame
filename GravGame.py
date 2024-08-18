import pygame
import sys
from random import randint

# Инициализация Pygame
pygame.init()

# Параметры экрана
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
	def __init__(self, x, y, radius):
		self.position = (x, y)
		self.radius = radius
	
	def draw(self, screen):
		pygame.draw.circle(screen,COLOR_PLANET,self.position,self.radius)

# Главная игра
class Game:
	def __init__(self):
		self.state = GameState.TEMP
		self.buttons = [
			Button("REGEN", 750, 200, 100, 50, self.regen),
			Button("Quit", 750, 300, 100, 50, self.quit_game)
		]
		self.planets = []

	def regen(self):
		self.planets = []
		i = 0
		while i < 3:
			self.planets.append(Planet(randint(100,500), randint(100,500), randint(10,100)))
			i += 1

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

	def update(self):
		pass

	def draw(self):
		screen.fill(COLOR_BACKGROUND)

		for planet in self.planets:
			planet.draw(screen)

		for batton in self.buttons:
			batton.draw(screen)

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
