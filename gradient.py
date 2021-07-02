from pygame import Color
from pygame import Surface
from pygame.transform import scale

from type_defs import Size


class Gradient:
    """
    Represents a gradient from one colour to another
    """

    def __init__(self, start: Color, end: Color) -> None:
        self.start = start
        self.end = end

    def lerp(self, other, quotient):
        return Gradient(
            self.start.lerp(other.start, quotient),
            self.end.lerp(other.end, quotient),
        )

    def get_surface(self, size: Size, horizontal: bool = False):
        width, height = map(int, (*size,))
        x, y = (0, 1)
        max_value = height
        surface_size = (1, height)
        if horizontal:
            x, y = (1, 0)
            max_value = width
            surface_size = (width, 1)
        surface = Surface(surface_size).convert_alpha()
        for i in range(max_value):
            surface.set_at(
                (x * i, y * i),
                self.start.lerp(self.end, (i / max_value)),
            )
        return scale(surface, (width, height))
