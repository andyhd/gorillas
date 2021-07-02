import random

import pygame
from pygame import Rect
from pygame import Surface

from config import HEIGHT
from config import WIDTH


class Building(Rect):
    MAX_HEIGHT = 320
    MIN_HEIGHT = 20
    SKINS = [pygame.image.load(f"images/building{i}.png") for i in range(1, 4)]
    WIDTH = 80
    TILE_HEIGHT = 20

    def __init__(self, *args, **kwargs) -> None:
        self.skin = Building.SKINS[kwargs.pop("skin", 0)]
        super().__init__(*args, **kwargs)

    @classmethod
    def random_list(cls, num_buildings: int) -> list["Building"]:
        buildings = []
        for x in range(num_buildings):
            height = random.randint(Building.MIN_HEIGHT, Building.MAX_HEIGHT)
            buildings.append(
                Building(
                    (x * Building.WIDTH, HEIGHT - height),
                    (Building.WIDTH, height),
                    skin=random.randint(0, 2),
                )
            )
        return buildings

    def render(self, surface) -> None:
        for y in range(self.y, self.y + self.height, Building.TILE_HEIGHT):
            surface.blit(self.skin, (self.x, y))


class Skyline:
    def __init__(self):
        self.buildings = []
        self.mask = None
        self.rect = Rect((0, 0), (WIDTH, HEIGHT))
        self.surface = None
        self.num_buildings = 10
        self.generate_buildings()

    def generate_buildings(self):
        self.buildings = Building.random_list(self.num_buildings)
        self.surface = Surface((WIDTH, HEIGHT))
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
