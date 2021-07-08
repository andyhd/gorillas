import random

import pygame
from pygame import Color
from pygame import Rect
from pygame import Surface
from pygame.math import Vector2

from config import HEIGHT
from config import WIDTH
from event import Event
from event import EventSource
from particle import age
from particle import boundary
from particle import Emitter
from particle import fade_out
from particle import gravity
from particle import growth
from particle import lifetime
from particle import Particle
from particle import ParticleStream
from type_defs import Vector


class Explosion:
    HEIGHT = 64
    WIDTH = 64

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


class ExplosionEmitter(Emitter, EventSource):
    def __init__(self, pos: Vector) -> None:
        super().__init__(pos)
        self.done = Event()
        self.add_stream(
            explosion_debris(
                bounds=Rect(0, -HEIGHT, WIDTH, HEIGHT * 2),
                callback=self.kill,
            ),
            pre_fill=100,
        )
        self.add_stream(
            explosion_flames(),
            pre_fill=100,
        )

    def kill(self):
        self.done(self)


def explosion_debris(bounds, callback) -> ParticleStream:
    """
    Particle factory for explosion debris
    """

    count = 100
    particles = []

    def decrement_count(particles):
        def _dec(p):
            particles.remove(p)
            if len(p) == 0:
                callback()

    for _ in range(count):
        p = Particle(
            colour=Color(255, 255, 255),
            size=Vector2(2, 2),
            forces=(
                gravity(),
                age(1),
                fade_out(3),
                lifetime(3),
                boundary(bounds, callback=decrement_count(particles)),
            ),
            velocity=Vector2(random.randint(0, 50), 0).rotate(random.randint(0, 360)),
        )
        particles.append(p)

    yield particles

    while count:
        yield []


def explosion_flames():
    flame_colours = (
        Color(226, 118, 18),
        Color(227, 222, 18),
    )
    yield [
        Particle(
            colour=flame_colours[0].lerp(flame_colours[1], random.random()),
            forces=(
                age(1),
                growth(-200),
                lifetime(1.5),
            ),
            velocity=Vector2(random.randint(10, 40), 0).rotate(random.randint(0, 360)),
            size=random.randint(100, 200),
        )
        for _ in range(100)
    ]

    while True:
        yield []
