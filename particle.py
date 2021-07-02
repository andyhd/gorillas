import math
import sys
from functools import cached_property
from itertools import islice
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Union

import pygame
from pygame import Color
from pygame import Rect
from pygame.math import Vector2

from animation import Timeline
from config import SPEED_FUDGE
from type_defs import Translation
from type_defs import Vector
from util import identity_translation
from util import rotate


Callback = Callable[["Particle"], None]
Force = Callable[["Particle", float], None]
ParticleFactory = Iterable[Iterable["Particle"]]


class Particle:
    """
    A particle with position, size, velocity, age, and optional colour, mass and a
    surface for rendering.
    May be influenced by a number of Forces, which are applied in sequence at update.
    """

    def __init__(
        self,
        pos: Optional[Vector2] = None,
        size: Optional[Vector2] = None,
        velocity: Optional[Vector2] = None,
        angle: float = 0,
        colour: Optional[Color] = None,
        surface=None,
        mass: float = 0,
        forces: Optional[Iterable[Force]] = None,
    ) -> None:
        self.pos = pos or Vector2(0, 0)
        self.velocity = velocity or Vector2(0, 0)
        self.colour = colour
        self._original_surface = surface
        if surface:
            self.rect = surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.size = size or Vector2(1, 1)
        self.angle = angle
        self.mass = mass
        self.forces = list(forces) if forces is not None else []
        self.age: float = 0

    @property
    def topleft(self):
        return self.pos - self.size / 2

    @property
    def rect(self):
        return Rect(self.topleft, self.size)

    @rect.setter
    def rect(self, *args):
        rect = Rect(*args)
        self.pos = Vector2(rect.center)
        self.size = Vector2(rect.size)

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, angle: float) -> None:
        self._angle = angle

        if not self._original_surface:
            return

        self._update_surface()

        self.size = Vector2(self.surface.get_size())

    def update(self, dt: float) -> None:
        for force in self.forces:
            force(self, dt)

        self.pos += self.velocity * dt * SPEED_FUDGE

    def kill(self) -> None:
        self.age = -1

    @property
    def killed(self) -> bool:
        return self.age == -1

    def render(self, surface, translate: Translation = identity_translation) -> None:
        if self.surface:
            surface.blit(self.surface, translate(self.topleft))
        else:
            pygame.draw.circle(
                surface,
                self.colour,
                translate(self.pos),
                max(*self.size),
            )

    @cached_property
    def surface(self):
        if not self._original_surface:
            return None

        if self.angle % 360 == 0:
            return self._original_surface

        return pygame.transform.rotate(self._original_surface, self.angle)

    def set_surface(self, value) -> None:
        self._original_surface = value
        self._update_surface()

    def _update_surface(self):
        if self._original_surface:
            try:
                del self.surface
            except AttributeError:
                pass

    @property
    def mask(self):
        if self.surface:
            return pygame.mask.from_surface(self.surface)


class Emitter:
    """
    Continuously creates and updates particles specified by factory functions
    """

    def __init__(
        self, pos: Optional[Vector] = None, max_particles: int = sys.maxsize
    ) -> None:
        self.particles: list[Particle] = []
        self.pos = Vector2(0, 0)
        if pos:
            self.pos = Vector2(*pos)
        self.max_particles = max_particles
        self.factories: list[ParticleFactory] = []

    def add_factory(self, factory: ParticleFactory, pre_fill: int = 0) -> None:
        self.factories.append(factory)
        for particles in islice(factory, pre_fill):
            for p in particles:
                if len(self.particles) < self.max_particles:
                    p.pos += self.pos
                    self.particles.append(p)

    def update(self, dt: float) -> None:
        for factory in self.factories:
            for p in next(factory):
                if len(self.particles) < self.max_particles:
                    p.pos += self.pos
                    self.particles.append(p)

        for p in self.particles[:]:
            p.update(dt)
            if p.killed:
                self.particles.remove(p)

    def render(
        self, surface, camera_translate_fn: Optional[Translation] = None
    ) -> None:
        if camera_translate_fn is None:
            camera_translate_fn = identity_translation
        for p in self.particles:
            p.render(surface, camera_translate_fn)


def age(amount: float) -> Force:
    """
    Ages particles at a specified rate
    """

    def _age(particle: Particle, dt: float) -> None:
        particle.age += amount * dt

    return _age


def gravity(accel: Vector = (0, 9.8)) -> Force:
    """
    Applies a fixed acceleration to particles
    """

    def _gravity(particle: Particle, dt: float) -> None:
        particle.velocity += Vector2(*accel) * dt * SPEED_FUDGE

    return _gravity


def colour_change(timeline: Timeline) -> Force:
    """
    Change particle colour based on its age and the specified timeline
    """

    def _change_colour(particle: Particle, _) -> None:
        particle.colour = timeline.at(particle.age)

    return _change_colour


def growth(amount: Union[float, Vector]) -> Force:
    """
    Grow or shrink a particle at a specified rate
    """

    def _grow(particle: Particle, dt: float) -> None:
        particle.size += amount * dt

    return _grow


def spin(degrees: float) -> Force:
    """
    Spin a particle a specified number of degrees
    """

    def _spin(particle: Particle, dt: float) -> None:
        particle.angle += degrees

    return _spin


def boundary(
    rect: Rect, inside: bool = True, callback: Optional[Callback] = None
) -> Force:
    """
    Kill particles that fall outside or inside the specified bounding Rect
    """

    def _oob(particle: Particle, _) -> None:
        particle_in_rect = rect.collidepoint(*particle.pos)

        if (inside and not particle_in_rect) or (not inside and particle_in_rect):
            if callable(callback):
                callback(particle)
            particle.kill()

    return _oob


def collide_mask(other, callback: Optional[Callback] = None) -> Force:
    """
    Kill particles that collide with the specified entity mask
    """

    def _mask(particle: Particle, _) -> None:
        if not other.rect.colliderect(particle.rect):
            return

        if other.mask.overlap(
            particle.mask,
            (particle.rect.left - other.rect.left, particle.rect.top - other.rect.top),
        ):
            if callable(callback):
                callback(particle)
            particle.kill()

    return _mask


def lifetime(max_age: float, callback: Optional[Callback] = None) -> Force:
    """
    Kills particles at a specified age
    """

    def _lifetime(particle: Particle, _) -> None:
        if particle.age >= max_age:
            if callable(callback):
                callback(particle)
            particle.kill()

    return _lifetime
