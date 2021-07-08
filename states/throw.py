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
from states.base import GameState
from world import World


class Throw(GameState):
    def __init__(self, world: World) -> None:
        self.start = Event()
        self.done = Event()
        self.hit_gorilla = Event()
        self.world = world
        self.banana_emitter = Emitter(max_particles=1)
        self.banana_emitter.add_stream(self.banana_factory())
        self.banana_img = pygame.image.load("images/banana.png").convert_alpha()
        self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.throw_sound = pygame.mixer.Sound("sounds/throw.wav")

        self.on_start(self.launch_banana)
        self.on_done(self.reset)

    @property
    def opponent(self):
        return self.world.gorillas[(self.world.current_player + 1) % 2]

    def reset(self):
        self.world.emitters.remove(self.banana_emitter)

    def banana_factory(self):
        while True:
            yield [
                Particle(
                    velocity=Vector2(
                        self.world.power * math.cos(self.world.angle),
                        -1 * self.world.power * math.sin(self.world.angle),
                    ),
                    forces=(
                        self.world.wind,
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
        self.done()

    def hit_skyline(self, particle: Particle) -> None:
        self.world.add_explosion(particle.pos)
        self.hit_sound.play()
        self.done()

    def hit_opponent(self, _) -> None:
        self.hit_gorilla(self.world.current_player)
        self.hit_sound.play()
        self.done()

    def render(self, surface) -> None:
        self.world.render(surface)

    def update(self, dt) -> None:
        self.world.update(dt)

    def launch_banana(self) -> None:
        gorilla = self.world.gorillas[self.world.current_player]
        self.banana_emitter.pos = gorilla.pos
        self.world.emitters.append(self.banana_emitter)
        self.throw_sound.play()
