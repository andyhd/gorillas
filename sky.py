import math
import random
from functools import cached_property
from typing import Iterable

from pygame import Color
from pygame import draw
from pygame import Rect
from pygame import Surface
from pygame.constants import HWSURFACE
from pygame.constants import SRCALPHA

from animation import Timeline
from gradient import Gradient
from particle import boundary
from particle import drag
from particle import Particle
from wind import Wind


class Sky:
    """
    A gradient sky background with colours determined by the specified time
    """

    # hours after midnight
    SUNRISE_START = 4
    SUNRISE_SWITCH = 6
    SUNRISE_END = 8
    NOON = 12
    SUNSET_START = 18
    SUNSET_SWITCH = 20
    SUNSET_END = 22

    DAY_BLUE = Color(76, 153, 255)
    DAY_WHITE = Color(255, 255, 255)
    DAWN_PURPLE = Color(204, 153, 255)
    DAWN_YELLOW = Color(255, 229, 153)
    NIGHT_BLACK = Color(0, 25, 76)
    NIGHT_BLUE = Color(51, 153, 255)
    SUNSET_PINK = Color(255, 153, 204)
    SUNSET_ORANGE = Color(255, 204, 51)

    gradient = Timeline(
        (SUNRISE_START, Gradient(NIGHT_BLACK, NIGHT_BLUE)),
        (SUNRISE_SWITCH, Gradient(DAWN_PURPLE, DAWN_YELLOW)),
        (SUNRISE_END, Gradient(DAY_BLUE, DAY_WHITE)),
        (SUNSET_START, Gradient(DAY_BLUE, DAY_WHITE)),
        (SUNSET_SWITCH, Gradient(SUNSET_PINK, SUNSET_ORANGE)),
        (SUNSET_END, Gradient(NIGHT_BLACK, NIGHT_BLUE)),
    )

    star_alpha = Timeline(
        (SUNSET_SWITCH, 0.0),
        (SUNSET_END, 1.0),
        (SUNRISE_START, 1.0),
        (SUNRISE_SWITCH, 0.0),
    )

    def __init__(self, width: int, height: int, time: float = NOON) -> None:
        self.width = width
        self.height = height
        self.time = time

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value % 24
        try:
            del self.surface
        except AttributeError:
            pass

    @cached_property
    def surface(self):
        surface = self.gradient.at(self.time).get_surface((self.width, self.height))
        star_alpha = self.star_alpha.at(self.time)
        if star_alpha > 0.0:
            stars = StarField(self.width, self.height)
            stars.surface.set_alpha(star_alpha * 255)
            surface.blit(stars.surface, (0, 0))

        return surface


class StarField:
    """
    A randomly generated field of stars
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        num_stars = int(width * height * 0.0005)
        self.surface = Surface((width, height)).convert_alpha()

        for _ in range(num_stars):
            pos = (random.randint(0, width), random.randint(0, height))
            brightness = random.randint(1, 4)
            if brightness < 4:
                self.surface.set_at(pos, Color(255, 255, 255, 63 + brightness * 64))
            else:
                draw.circle(
                    self.surface,
                    Color(255, 255, 255),
                    pos,
                    1,
                    width=0,
                )


class Cloud:
    """
    Procedurally generated cloud
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        half_width = width / 2
        margin = int(max(1, width / 10))
        self.surface = Surface(
            (width, height),
            flags=HWSURFACE,
        ).convert_alpha()

        for _ in range(random.randint(20, 40)):
            x = random.randrange(margin, width - margin)
            dist_from_center = abs(half_width - x)
            scale = random.random() + 2 * math.sin(1 / (dist_from_center + 1))
            y = height - 2
            r = max(1, margin * scale)
            draw.circle(self.surface, Color(255, 255, 255), (x, y), r, width=0)


def make_cloud_particle(wind: Wind, bounds: Rect) -> Particle:
    cloud = Cloud(random.randrange(100, 300), 100)
    return Particle(
        surface=cloud.surface,
        mass=1,
        alpha=128,
        drag_coefficient=random.uniform(0.4, 0.8),
        forces=(
            wind.drag,
            boundary(bounds),
        ),
    )


def clouds(wind: Wind, bounds: Rect) -> Iterable[Iterable[Particle]]:
    while True:
        if random.random() < 0.95:
            p = make_cloud_particle(wind, bounds)
            p.pos.y = random.randrange(60, int(bounds.height / 4))
            p.pos.x = bounds.left
            if wind.direction < 0:
                p.pos.x = bounds.right - 1
            yield [p]
        else:
            yield []
