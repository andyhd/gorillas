import math
from functools import cached_property

import pygame
from pygame import Color
from pygame import Rect
from pygame import Surface
from pygame.math import Vector2

from config import HEIGHT
from config import WIDTH
from gradient import Gradient
from progress_bar import ProgressBar
from type_defs import Size
from type_defs import Vector
from wind import Wind


class HealthBar(ProgressBar):
    def __init__(self, pos: Vector, size: Size, max_value: float, flip=False) -> None:
        gradient = Gradient(
            Color(255, 0, 0),
            Color(255, 255, 0),
        )
        super().__init__(
            pos,
            gradient.get_surface(size, horizontal=True),
            max_value,
            flip=flip,
        )


class Scoreboard:
    def __init__(self):
        self.scores = [0, 0]
        self.healthbars = [
            HealthBar((0, 16), (200, 32), 3),
            HealthBar((WIDTH - 200, 16), (200, 32), 3, flip=True),
        ]

    def __iter__(self):
        return iter(self.scores)

    def render(self, surface):
        for healthbar in self.healthbars:
            surface.blit(healthbar.surface, healthbar.rect.topleft)

    def add_score(self, index, value=1):
        self.scores[index] += value
        self.healthbars[(index + 1) % 2].value -= 1

    def reset(self):
        self.scores = [0, 0]
        for healthbar in self.healthbars:
            healthbar.value = 3


class HotseatIndicator:
    def __init__(self):
        self.angle = 0
        self.surface = pygame.image.load("images/hotseat.png").convert_alpha()
        self.pos = Vector2(0, 0)

    def update(self, dt):
        self.angle = (self.angle + 360 * dt) % 360
        self.pos.y += math.sin(math.radians(self.angle)) * 2

    def render(self, surface):
        surface.blit(self.surface, self.pos)


class WindGauge:
    """
    A UI component displaying wind speed and direction
    """

    def __init__(self, pos: Vector, size: Size, wind: Wind) -> None:
        self.wind = wind
        gradient = Gradient(
            Color(0, 255, 0),
            Color(255, 0, 0),
        )
        self.rect = Rect(*pos, *size)
        self.bar = ProgressBar(
            pos,
            gradient.get_surface(
                (self.rect.width / 2, self.rect.height), horizontal=True
            ),
            self.wind.max_speed,
        )
        self.redraw()

        self.wind.on_changed(self.redraw)

    def render(self, surface) -> None:
        surface.blit(self.surface, self.rect.topleft)

    def redraw(self) -> None:
        try:
            del self.surface
        except AttributeError:
            pass

        self.bar.value = self.wind.speed
        self.bar.flip = self.wind.direction < 0

    @cached_property
    def surface(self):
        surface = Surface(self.rect.size)
        x = 0 if self.bar.flip else self.rect.width / 2
        surface.blit(self.bar.surface, (x, 0))

        pygame.draw.rect(
            surface,
            Color(255, 255, 255),
            Rect((0, 0), self.rect.size),
            width=1,
        )
        pygame.draw.line(
            surface,
            Color(255, 255, 255),
            (self.rect.width / 2, 0),
            (self.rect.width / 2, self.rect.height),
        )
        return surface
