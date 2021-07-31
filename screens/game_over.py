import pygame

from config import HEIGHT
from config import WIDTH
from event import Event
from screens.base import Screen


class GameOver(Screen):
    def __init__(self) -> None:
        super().__init__()
        font = pygame.font.Font(None, 24)
        label = font.render("GAME OVER", True, (255, 255, 255))
        rect = label.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.surface.fill((0, 0, 0))
        self.surface.blit(label, rect.topleft)

    def on_key_up(self, *_) -> None:
        self.exit()
