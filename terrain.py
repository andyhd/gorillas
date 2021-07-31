import random
from enum import Enum

import pygame
from pygame import Color
from pygame import Rect
from pygame import Surface

from config import HEIGHT
from config import WIDTH
from util import tile


class Building(Rect):
    """
    Procedurally generated building.

    Variables:

    * Height - min and max limits - should difference between neighbours be
    limited?
    * Width - min and max limits
    * Materials (brick, stone, concrete, pebbledash)
    * Colour - limited by material
    * Usage type - housing, commercial - should buildings be grouped by type?
    * Window placement - affected by usage - what is inside?
        * people
        * lights
        * curtains/blinds
        * broken glass
        * boarded up
        * commercial signs
    * Decorations - affected by usage
        * Mouldings
        * Billboards, neon signs
        * Aerials
        * Fire escape
        * Water tower
        * AC units
        * Red flashing light on tallest buildings
        * Window washers

    Data driven:
        types of buildings are lists of parameters for building factory
        can be loaded from JSON file?
    """

    MAX_HEIGHT = 320
    MIN_HEIGHT = 20
    MIN_WIDTH = 80
    MAX_WIDTH = 240

    class Material(Enum):
        BRICK = 1
        # STONE = 2
        CONCRETE = 3

    class Usage(Enum):
        COMMERCIAL = 1
        RESIDENTIAL = 2

    def __init__(self, *args, material=Material.BRICK, variant=1, **kwargs):
        self.windows = kwargs.pop("windows", None)
        super().__init__(*args, **kwargs)
        self.material = material
        self.texture = pygame.image.load(
            f"images/building_tex_{material.value}_{variant}.png"
        )

    @classmethod
    def random_list(cls, max_width: int = WIDTH) -> list["Building"]:
        widths = []
        remaining = max_width
        while remaining > Building.MIN_WIDTH:
            width = random.randrange(
                Building.MIN_WIDTH, min(Building.MAX_WIDTH, remaining)
            )
            remaining -= width
            widths.append(width)

        if remaining:
            num_widths = len(widths)
            middle = num_widths // 2
            for i in range(middle):
                index = middle - i
                if index >= 0 and widths[index] + remaining < Building.MAX_WIDTH:
                    widths[index] += remaining
                    break
                index = middle + i
                if (
                    index < num_widths
                    and widths[index] + remaining < Building.MAX_WIDTH
                ):
                    widths[index] += remaining
                    break

        x = 0
        for width in widths:
            height = random.randrange(Building.MIN_HEIGHT, Building.MAX_HEIGHT)
            yield Building(
                x,
                HEIGHT - height,
                width,
                height,
                material=random.choice(list(Building.Material)),
                variant=random.choice([1, 2, 3, 4]),
                windows=(
                    Interval(random.randint(0, width // 40), random.uniform(0.6, 0.9))
                    & Interval(
                        random.randint(0, height // 40), random.uniform(0.6, 0.9)
                    )
                ),
            )
            x += width

    def render(self, surface) -> None:
        tile(surface, self.texture, self)

        if self.windows:
            for left, top, width, height in self.windows:
                window = Rect(
                    int(left * self.width) + self.left,
                    int(top * self.height) + self.top,
                    int(width * self.width),
                    int(height * self.height),
                )
                pygame.draw.rect(
                    surface,
                    Color(0, 0, 0),
                    window,
                )
                pygame.draw.rect(
                    surface,
                    Color(200, 200, 200),
                    window,
                    width=2,
                )


class Skyline:
    def __init__(self):
        self.buildings = []
        self.mask = None
        self.rect = Rect((0, 0), (WIDTH, HEIGHT))
        self.surface = None
        self.num_buildings = 10
        self.generate_buildings()

    def generate_buildings(self):
        self.buildings = list(Building.random_list(WIDTH))
        self.surface = Surface((WIDTH, HEIGHT)).convert_alpha()
        for building in self.buildings:
            building.render(self.surface)
        self.mask = pygame.mask.from_surface(self.surface)

    def render(self, surface) -> None:
        surface.blit(
            self.mask.to_surface(
                unsetcolor=None,
                setsurface=self.surface,
            ),
            (0, 0),
        )

    def destroy(self, other):
        self.mask.erase(other.mask, (int(other.rect.left), int(other.rect.top)))


class Interval:
    def __init__(self, frequency: int, duty_cycle: float = 0.5):
        self.frequency = frequency
        self.wavelength = 1.0 / frequency if frequency else 1.0
        self.duty_cycle = duty_cycle * self.wavelength
        self.margin = (self.wavelength - self.duty_cycle) / 2.0

    def __iter__(self):
        for i in range(self.frequency):
            yield (i * self.wavelength + self.margin, self.duty_cycle)

    def __and__(self, other):
        for top, height in self:
            for left, width in other:
                yield (left, top, width, height)
