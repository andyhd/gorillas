from functools import cached_property

from pygame import Rect
from pygame import Surface
from pygame import transform

from type_defs import Vector


class ProgressBar:
    def __init__(
        self,
        pos: Vector,
        surface,
        max_value: float = 100.0,
        flip=False,
    ) -> None:
        self._surface = surface
        self.size = surface.get_size()
        self.pos = pos
        self.rect = Rect(*pos, *self.size)
        self.max_value = max_value
        self._value = max_value
        self.flip = flip

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float):
        self._value = value
        try:
            del self.surface
        except AttributeError:
            pass

    @property
    def cliprect(self) -> Rect:
        width, height = self.size
        progress_width = width * (self.value / self.max_value)
        return Rect(0, 0, progress_width, height)

    @cached_property
    def surface(self):
        surface = Surface(self.size).convert_alpha()
        surface.blit(self._surface, (0, 0), self.cliprect)
        if self.flip:
            surface = transform.flip(surface, True, False)
        return surface
