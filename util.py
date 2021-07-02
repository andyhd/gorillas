from typing import Optional

from pygame import transform
from pygame.math import Vector2

from type_defs import Translation
from type_defs import Vector


def rotate(surface, angle, pivot, offset):
    rotated_surface = transform.rotate(surface, angle)
    rotated_offset = Vector2(offset).rotate(-angle)
    rect = rotated_surface.get_rect(center=pivot + rotated_offset)
    return rotated_surface, rect


def identity_translation(coord: Vector) -> Vector:
    return coord


class Renderable:
    def render(self, surface, translate: Optional[Translation] = None) -> None:
        if translate is None:
            translate = identity_translation

        surface.blit(self.surface, translate(self.rect.topleft))
