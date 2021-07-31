import pygame

from screens.base import Screen


class MainMenu(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.surface.blit(pygame.image.load("images/menu.png"), (0, 0))

    def on_key_up(self, *_) -> None:
        self.exit()
