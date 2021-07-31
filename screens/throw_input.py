import math

import pygame
from pygame import Color
from pygame import Rect

from config import HEIGHT
from config import WIDTH
from gorilla import Gorilla
from screens.base import Screen
from util import rotate


class ThrowInput(Screen):
    RETICLE_WIDTH = 32

    def __init__(self, world) -> None:
        super().__init__()

        self.change_per_second = 100
        self.direction = 1
        self.angle_input = 0
        self.power_input = 10
        self.min_power = 10
        self.max_power = 200
        self.pulse_power = False
        self.reticle = pygame.image.load("images/reticle.png")
        self.powerbar = pygame.image.load("images/powerbar.png")
        self.font = pygame.font.Font(None, 24)
        self.text = ""
        self.text_surface = None
        self.world = world

    def render(self, surface) -> None:
        self.world.render(self.surface)

        gorilla = self.world.gorillas[self.world.current_player]
        angle = int(self.angle_input * (180 / math.pi))
        if self.world.current_player == 1:
            angle = 180 - angle
        power = int(self.power_input)

        pygame.draw.rect(
            self.surface,
            Color(0, 0, 0),
            Rect((0, 0), (WIDTH, 16)),
        )
        text = f"Angle: {str(angle)}, Power: {str(power)}"
        if text != self.text:
            self.text = text
            self.text_surface = self.font.render(
                text,
                True,
                Color(255, 255, 255),
            )
        self.surface.blit(self.text_surface, (0, 0))

        angle_x = math.cos(self.angle_input)
        angle_y = math.sin(self.angle_input)

        reticle_pos = (
            gorilla.pos.x + angle_x * Gorilla.WIDTH - self.RETICLE_WIDTH / 2,
            gorilla.pos.y - angle_y * Gorilla.WIDTH - self.RETICLE_WIDTH / 2,
        )
        self.surface.blit(self.reticle, reticle_pos)

        if self.pulse_power:
            half_width = Gorilla.WIDTH / 2
            powerbar_length = (self.power_input / self.max_power) * half_width
            powerbar = self.powerbar.subsurface(
                Rect((0, 0), (half_width + powerbar_length, Gorilla.HEIGHT)),
            ).copy()
            powerbar, rect = rotate(
                powerbar,
                int(self.angle_input * (180 / math.pi)),
                gorilla.rect.center,
                (powerbar_length / 2 + 16, 0),
            )
            self.surface.blit(
                powerbar,
                rect.topleft,
            )

        super().render(surface)

    def update(self, dt) -> None:
        self.world.update(dt)
        if self.pulse_power:
            self.power_input += self.change_per_second * dt * self.direction
            if self.power_input < self.min_power:
                self.power_input = 2 * self.min_power - self.power_input
                self.direction = 1
            if self.power_input > self.max_power:
                self.power_input = 2 * self.max_power - self.power_input
                self.direction = -1

    def set_angle_from_mouse_pos(self, pos):
        x, y = pos
        gorilla = self.world.gorillas[self.world.current_player]
        self.angle_input = math.atan2(gorilla.pos.y - y, x - gorilla.pos.x)

    def reset_angle(self, *_):
        self.set_angle_from_mouse_pos(pygame.mouse.get_pos())

    def on_mouse_move(self, pos, rel, buttons):
        self.set_angle_from_mouse_pos(pos)

    def on_mouse_down(self, pos, button):
        self.pulse_power = True
        self.power_input = self.min_power

    def on_mouse_up(self, pos, button):
        self.pulse_power = False
        self.exit(self.angle_input, self.power_input)
