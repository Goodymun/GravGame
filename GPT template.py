 # -*- coding: utf8 -*-

import pygame
import sys

# ������������� Pygame
pygame.init()

# ��������� ������
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Game Template")

# �����
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# ��������� ����
class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    GAME_OVER = 'game_over'

# ����� ������
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                   self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ������� ����
class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.buttons = [
            Button("Start Game", 300, 200, 200, 50, self.start_game),
            Button("Quit", 300, 300, 200, 50, self.quit_game)
        ]
        self.player = pygame.Rect(50, 50, 50, 50)  # �����
        self.player_speed = 5

    def start_game(self):
        self.state = GameState.PLAYING

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

            if self.state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.is_clicked(event.pos):
                            button.callback()

            if self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

    def update(self):
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.x -= self.player_speed
            if keys[pygame.K_RIGHT]:
                self.player.x += self.player_speed
            if keys[pygame.K_UP]:
                self.player.y -= self.player_speed
            if keys[pygame.K_DOWN]:
                self.player.y += self.player_speed

    def draw(self):
        screen.fill(BLACK)

        if self.state == GameState.MENU:
            for button in self.buttons:
                button.draw(screen)

        elif self.state == GameState.PLAYING:
            pygame.draw.rect(screen, GREEN, self.player)

        elif self.state == GameState.GAME_OVER:
            font = pygame.font.Font(None, 74)
            text_surface = font.render("Game Over", True, WHITE)
            screen.blit(text_surface, ((WIDTH - text_surface.get_width()) // 2, (HEIGHT - text_surface.get_height()) // 2))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
