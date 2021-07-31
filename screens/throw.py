import math

import pygame
from pygame import Rect
from pygame.math import Vector2

from config import HEIGHT
from config import WIDTH
from event import Event
from particle import boundary
from particle import collide_mask
from particle import Emitter
from particle import gravity
from particle import Particle
from particle import spin
from screens.base import Screen
from world import World


class Throw(Screen):
    def __init__(self, world: World) -> None:
        super().__init__()

        self.hit_gorilla = Event()
        self.world = world
        self.banana_emitter = Emitter(max_particles=1)
        self.banana_emitter.add_stream(self.banana_factory())
        self.banana_img = pygame.image.load("images/banana.png").convert_alpha()
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.throw_sound = pygame.mixer.Sound("sounds/throw.wav")

        self.on_enter(self.launch_banana)
        self.on_exit(self.reset)

    @property
    def opponent(self):
        return self.world.gorillas[(self.world.current_player + 1) % 2]

    def reset(self):
        try:
            self.world.emitters.remove(self.banana_emitter)
        except ValueError:
            pass

    def banana_factory(self):
        while True:
            yield [
                Particle(
                    velocity=Vector2(
                        self.world.power * math.cos(self.world.angle),
                        -1 * self.world.power * math.sin(self.world.angle),
                    ),
                    mass=2,
                    drag_coefficient=0.3,
                    forces=(
                        self.world.wind.drag,
                        boundary(
                            Rect(0, -HEIGHT, WIDTH, HEIGHT * 2),
                            callback=self.out_of_bounds,
                        ),
                        collide_mask(self.world.skyline, callback=self.hit_skyline),
                        collide_mask(self.opponent, callback=self.hit_opponent),
                        gravity(),
                        spin(5),
                    ),
                    surface=self.banana_img,
                )
            ]

    def out_of_bounds(self, *_) -> None:
        self.exit()

    def hit_skyline(self, particle: Particle) -> None:
        self.world.add_explosion(particle.pos)
        self.hit_sound.play()
        self.exit()

    def hit_opponent(self, _) -> None:
        self.hit_gorilla(self.world.current_player)
        self.hit_sound.play()
        self.exit()

    def render(self, surface) -> None:
        self.world.render(self.surface)
        super().render(surface)

    def update(self, dt) -> None:
        self.world.update(dt)

    def launch_banana(self) -> None:
        gorilla = self.world.gorillas[self.world.current_player]
        self.banana_emitter.pos = gorilla.pos
        self.world.emitters.append(self.banana_emitter)
        self.throw_sound.play()
