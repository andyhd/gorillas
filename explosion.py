import pygame
from pygame import Color
from pygame import Surface
from pygame.math import Vector2

from type_defs import Vector


class Explosion:
    HEIGHT = 32
    WIDTH = 32

    def __init__(self, pos: Vector) -> None:
        self.surface = Surface((self.WIDTH, self.HEIGHT))
        pygame.draw.circle(
            self.surface,
            Color(255, 255, 255),
            (self.WIDTH / 2, self.HEIGHT / 2),
            self.WIDTH / 2,
            width=0,
        )
        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect(center=pos)
        self.pos = Vector2(*pos)
