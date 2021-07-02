import pygame

from config import HEIGHT
from config import WIDTH
from event import Event
from states.base import GameState


class GameOver(GameState):
    def __init__(self) -> None:
        self.done = Event()
        font = pygame.font.Font(None, 24)
        self.surface = font.render("GAME OVER", True, (255, 255, 255))
        self.rect = self.surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))

    def render(self, surface) -> None:
        surface.fill((0, 0, 0))
        surface.blit(self.surface, self.rect.topleft)

    def on_key_up(self, *_) -> None:
        self.done()
