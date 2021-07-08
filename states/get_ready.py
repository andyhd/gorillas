import pygame
from pygame import Color
from pygame import Rect
from pygame.math import Vector2

from animation import Timeline
from config import HEIGHT
from config import WIDTH
from event import Event
from states.base import GameState
from world import World


class GetReady(GameState):
    def __init__(self, world: World) -> None:
        self.done = Event()
        self.world = world
        self.timer = 0
        self.max_time = 3
        self.bar_pos = Timeline(
            (0, Vector2(0, HEIGHT / 2)),
            (1, Vector2(0, HEIGHT / 2 - 46)),
            (2, Vector2(0, HEIGHT / 2 - 46)),
            (3, Vector2(0, HEIGHT / 2)),
        )
        self.bar_size = Timeline(
            (0, Vector2(WIDTH, 1)),
            (1, Vector2(WIDTH, 92)),
            (2, Vector2(WIDTH, 92)),
            (3, Vector2(WIDTH, 1)),
        )

        self.get_ready = [
            pygame.image.load("images/get_ready_player_1.png"),
            pygame.image.load("images/get_ready_player_2.png"),
        ]
        image_width, image_height = self.get_ready[0].get_size()
        self.text_pos = Timeline(
            (0, Vector2(-image_width, (HEIGHT - image_height) / 2)),
            (1, Vector2((WIDTH - image_width) / 2, (HEIGHT - image_height) / 2)),
            (2, Vector2((WIDTH - image_width) / 2, (HEIGHT - image_height) / 2)),
            (3, Vector2(WIDTH, (HEIGHT - image_height) / 2)),
        )

    def start(self, *_):
        self.elapsed = 0

    def render(self, surface) -> None:
        self.world.render(surface)
        pygame.draw.rect(
            surface,
            Color(255, 0, 255),
            Rect(self.bar_pos.at(self.timer), self.bar_size.at(self.timer)),
        )
        surface.blit(
            self.get_ready[self.world.current_player],
            self.text_pos.at(self.timer),
        )

    def update(self, dt) -> None:
        self.world.update(dt)
        if not hasattr(self, "timer"):
            self.timer = 0
        self.timer += dt
        if self.timer > 3:
            self.done()
            self.timer = 0
