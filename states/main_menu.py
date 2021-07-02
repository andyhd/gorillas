import pygame

from event import Event
from states.base import GameState


class MainMenu(GameState):
    def __init__(self) -> None:
        self.done = Event()
        self.background = pygame.image.load("images/menu.png")

    def render(self, surface) -> None:
        surface.blit(self.background, (0, 0))

    def on_key_up(self, *_) -> None:
        self.done()
