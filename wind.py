import random
from typing import Iterable
from typing import Optional

from pygame import Color
from pygame import Rect

from config import SPEED_FUDGE
from event import Event
from event import EventSource
from particle import boundary
from particle import Particle


class Wind(EventSource):
    """
    A constant horizontal acceleration force on particles
    """

    def __init__(self, max_speed: float = 0):
        self.speed = 0
        self.direction = 0
        self.max_speed = max_speed
        self.changed = Event()

    def change(self, speed: Optional[float] = None, direction: Optional[int] = None):
        if speed is None:
            speed = random.uniform(0, self.max_speed)
        self.speed = speed
        if direction is None:
            direction = random.choice([-1, 1])
        self.direction = direction

        self.changed()

    def __call__(self, particle: Particle, dt: float) -> None:
        particle.velocity.x += dt * self.speed * self.direction * SPEED_FUDGE


def debris(wind: Wind, bounds: Rect) -> Iterable[Iterable[Particle]]:
    """
    Particle factory for wind-blown debris
    """

    while True:
        if random.uniform(0, wind.max_speed) < wind.speed and random.random() >= 0.9:
            p = Particle(
                colour=Color(0, 0, 0),
                forces=(wind, boundary(bounds)),
            )
            p.pos.y = random.randint(0, bounds.height)
            if wind.direction < 0:
                p.pos.x = bounds.width - 1
            yield [p]
        else:
            yield []
