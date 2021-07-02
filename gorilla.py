import pygame
from pygame.math import Vector2

from type_defs import Vector
from util import Renderable


class Gorilla(Renderable):
    HEIGHT = 64
    WIDTH = 64

    def __init__(self, pos: Vector) -> None:
        self.surface = pygame.image.load("images/gorilla.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect(center=pos)
        self.pos = Vector2(*pos)
