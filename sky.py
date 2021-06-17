import pygame


class Transition:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __contains__(self, value):
        return self.start <= value <= self.end

    def __iter__(self):
        yield self.start
        yield self.end

    def quotient(self, value):
        return ((value - self.start) / (self.end - self.start))


def interpolate(start, end, quotient):
    return start + quotient * (end - start)


class Sky:
    SUNSET_START = 70
    SUNSET_SWITCH = 80
    SUNSET_END = 87
    SUNRISE_START = 278
    SUNRISE_SWITCH = 281
    SUNRISE_END = 287

    DAY_BLUE = pygame.Color(76, 153, 255)
    DAY_WHITE = pygame.Color(255, 255, 255)
    DAWN_PURPLE = pygame.Color(204, 153, 255)
    DAWN_YELLOW = pygame.Color(255, 229, 153)
    NIGHT_BLACK = pygame.Color(0, 25, 76)
    NIGHT_BLUE = pygame.Color(51, 153, 255)
    SUNSET_PINK = pygame.Color(255, 153, 204)
    SUNSET_ORANGE = pygame.Color(255, 204, 51)

    DUSK = Transition(SUNSET_SWITCH, SUNSET_END)
    NIGHT = Transition(SUNSET_END, SUNRISE_START)
    DAWN = Transition(SUNRISE_START, SUNRISE_SWITCH)

    TRANSITIONS = (
        Transition(0, SUNSET_START),
        Transition(SUNSET_START, SUNSET_SWITCH),
        DUSK,
        NIGHT,
        DAWN,
        Transition(SUNRISE_SWITCH, SUNRISE_END),
        Transition(SUNRISE_END, 360),
    )

    GRADIENT_COLOURS = {
        0: (DAY_BLUE, DAY_WHITE),
        SUNSET_START: (DAY_BLUE, DAY_WHITE),
        SUNSET_SWITCH: (SUNSET_PINK, SUNSET_ORANGE),
        SUNSET_END: (NIGHT_BLACK, NIGHT_BLUE),
        SUNRISE_START: (NIGHT_BLACK, NIGHT_BLUE),
        SUNRISE_SWITCH: (DAWN_PURPLE, DAWN_YELLOW),
        SUNRISE_END: (DAY_BLUE, DAY_WHITE),
        360: (DAY_BLUE, DAY_WHITE),
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def gradient_colours(self, time):
        transition = next(t for t in self.TRANSITIONS if time in t)
        start, end = transition
        ratio = transition.quotient(time)

        top_start, bottom_start = self.GRADIENT_COLOURS[start]
        top_end, bottom_end = self.GRADIENT_COLOURS[end]

        return (
            top_start.lerp(top_end, ratio),
            bottom_start.lerp(bottom_end, ratio),
        )

    def gradient(self, time):
        surface = pygame.Surface((1, self.height)).convert_alpha()
        start, end = self.gradient_colours(time)
        for y in range(self.height):
            surface.set_at(
                (0, y),
                start.lerp(end, (y / self.height)),
            )
        return pygame.transform.scale(surface, (self.width, self.height))

    def star_alpha(self, time):
        for period, alpha_start, alpha_end in [
            (self.DUSK, 0.0, 1.0),
            (self.NIGHT, 1.0, 1.0),
            (self.DAWN, 1.0, 0.0),
        ]:
            if time in period:
                return interpolate(alpha_start, alpha_end, period.quotient(time))

        return 0.0
