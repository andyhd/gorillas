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
from pygame import Surface
from pygame.math import Vector2

from animation import Timeline
from config import SPEED_FUDGE
from type_defs import Translation
from type_defs import Vector
from util import identity_translation


Callback = Callable[["Particle"], None]
Force = Callable[["Particle", float], None]
ParticleStream = Iterable[Iterable["Particle"]]


class Particle:
    """
    A particle with position, size, velocity, age, and optional colour, mass and a
    surface for rendering.
    May be influenced by a number of Forces, which are applied in sequence at update.
    """

    def __init__(
        self,
        pos: Optional[Vector2] = None,
        size: Optional[Union[Vector2, int]] = None,
        velocity: Optional[Vector2] = None,
        angle: float = 0,
        scale: float = 1,
        colour: Optional[Color] = None,
        surface=None,
        mass: float = 0,
        alpha: Optional[float] = None,
        forces: Optional[Iterable[Force]] = None,
    ) -> None:
        self.pos = pos or Vector2(0, 0)
        self.velocity = velocity or Vector2(0, 0)
        self.alpha = 255 if alpha is None else alpha
        self.mass = mass
        self.forces = list(forces) if forces is not None else []
        self.age: float = 0

        self._original_surface = surface
        self._scale = scale
        self._angle = angle
        self._colour = colour

        if surface:
            self.size = Vector2(surface.get_size())
            self._scale = scale
            self._angle = angle

        else:
            if isinstance(size, int):
                self.size = Vector2(size, size)
            else:
                self.size = size or Vector2(1, 1)
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self._colour = colour or Color(255, 255, 255)

    @cached_property
    def surface(self):
        if self._original_surface:
            surface = pygame.transform.rotozoom(
                self._original_surface, self.angle, self.scale
            )

        else:
            surface = Surface(self.size * self.scale).convert_alpha()
            pygame.draw.circle(
                surface,
                self.colour,
                center=(self.size / 2) * self.scale,
                radius=(max(*self.size) / 2) * self.scale,
            )

        return surface

    @property
    def topleft(self):
        return self.pos - self.size / 2

    @property
    def rect(self):
        return Rect(self.topleft, self.size)

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, angle: float) -> None:
        self._angle = angle
        self._update_surface()
        self.size = Vector2(self.surface.get_size())

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, scale: float) -> None:
        self._scale = scale
        self._update_surface()
        self.size = Vector2(self.surface.get_size())

    @property
    def colour(self) -> Optional[Color]:
        return self._colour

    @colour.setter
    def colour(self, colour: Color) -> None:
        self._colour = colour
        self._update_surface()

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
        self.surface.set_alpha(int(self.alpha))
        surface.blit(self.surface, translate(self.topleft))

    def set_surface(self, value) -> None:
        self._original_surface = value
        self._update_surface()

    def _update_surface(self):
        try:
            del self.surface
        except AttributeError:
            pass

    @property
    def mask(self):
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
        self.streams: list[ParticleStream] = []

    def add_stream(self, stream: ParticleStream, pre_fill: int = 0) -> None:
        self.streams.append(stream)
        for particles in islice(stream, pre_fill):
            for p in particles:
                if len(self.particles) < self.max_particles:
                    p.pos += self.pos
                    self.particles.append(p)

    def update(self, dt: float) -> None:
        for stream in self.streams:
            for p in next(stream):
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


def drag(
    linear_coefficient: float,
    squared_coefficient: float = 0.0,
    fluid_velocity: Optional[Vector2] = None,
    domain: Optional[Rect] = None,
) -> Force:
    """
    Simulate viscous drag in a fluid
    """

    # a value close to zero used to avoid infinite forces
    epsilon = 0.00001

    if fluid_velocity is None:
        fluid_velocity = Vector2(0, 0)

    def _drag(particle: Particle, dt: float) -> None:
        if not particle.killed and (domain is None or domain.contains(particle.pos)):
            rvel = particle.velocity * dt - fluid_velocity * dt
            rmag = rvel.length_squared()
            if rmag > epsilon:
                drag = linear_coefficient * rmag + squared_coefficient * rmag * rmag
                force = ((rvel / rmag) * drag) / max(particle.mass, epsilon)
                particle.velocity -= force

    return _drag


def colour_change(timeline: Timeline) -> Force:
    """
    Change particle colour based on its age and the specified timeline
    """

    def _change_colour(particle: Particle, _) -> None:
        particle.colour = timeline.at(particle.age)

    return _change_colour


def fade_out(duration: float, start: float = 0.0) -> Force:
    """
    Change particle alpha to transparent based on age
    """

    alpha_gradient = Timeline(
        (start, 255),
        (start + duration, 0),
    )

    def _fade_out(particle: Particle, _) -> None:
        particle.alpha = alpha_gradient.at(particle.age)

    return _fade_out


def growth(amount: float) -> Force:
    """
    Grow or shrink a particle at a specified rate
    """

    def _grow(particle: Particle, dt: float) -> None:
        particle.scale = max(
            (particle.size.x + amount * dt) / max(particle.size.x, 0.00001), 0
        )

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
