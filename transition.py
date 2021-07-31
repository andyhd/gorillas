import pygame

import config
from animation import Timeline
from event import Event
from event import EventSource
from screens.base import Screen


class BaseTransition(EventSource):
    def __init__(self) -> None:
        self.from_screen = None
        self.to_screen = None
        self.exit = Event()

    def render(self, surface: pygame.Surface) -> None:
        self.to_screen.render(surface)

    def update(self, dt: float) -> None:
        self.to_screen.update(dt)
        self.exit()


class Wipe(BaseTransition):
    def __init__(self, duration: float) -> None:
        super().__init__()

        self.duration = duration

        self.timer = 0

        self.from_screen_x = Timeline(
            (0, 0),
            (duration, -config.WIDTH),
        )
        self.to_screen_x = Timeline(
            (0, config.WIDTH),
            (duration, 0),
        )
        self.from_surface = None
        self.to_surface = None

    def render(self, surface: pygame.Surface) -> None:
        if not self.from_surface:
            self.from_surface = surface.copy()
            self.from_screen.render(self.from_surface)
        if not self.to_surface:
            self.to_surface = surface.copy()
            self.to_screen.render(self.to_surface)
        surface.blit(
            self.from_surface,
            (self.from_screen_x.at(self.timer), 0),
        )
        surface.blit(
            self.to_surface,
            (self.to_screen_x.at(self.timer), 0),
        )

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer > self.duration:
            self.timer = 0
            self.exit()


class FadeToBlack(BaseTransition):
    def __init__(self, duration: float) -> None:
        super().__init__()
        self.duration = duration
        self.timer = 0
        self.alpha = Timeline(
            (0, 0),
            (duration, 255),
        )
        self.from_surface = None
        self.overlay = None

    def render(self, surface: pygame.Surface) -> None:
        if not self.from_surface:
            self.from_surface = surface.copy()
            self.from_screen.render(self.from_surface)

        if not self.overlay:
            self.overlay = pygame.Surface(self.from_surface.get_size())

        self.overlay.set_alpha(int(self.alpha.at(self.timer)))
        self.overlay.fill((0, 0, 0))
        surface.blit(self.from_surface, (0, 0))
        surface.blit(self.overlay, (0, 0))

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer > self.duration:
            self.timer = 0
            self.exit()
