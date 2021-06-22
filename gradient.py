from pygame import Color
from pygame import Surface
from pygame.transform import scale


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

    def get_surface(self, width, height):
        surface = Surface((1, height)).convert_alpha()
        for y in range(height):
            surface.set_at(
                (0, y),
                self.start.lerp(self.end, (y / height)),
            )
        return scale(surface, (width, height))
