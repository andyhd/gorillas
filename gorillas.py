import math
import random

import pygame
from pgzero.actor import Actor
from pgzero.keyboard import keys
from pgzero.rect import Rect
from pygame import Color
from pygame import Surface
from pygame.math import Vector2

from animation import Timeline
from event import Event
from event import EventSource
from gradient import Gradient
from sky import Sky
from state import State
from state import StateMachine


HEIGHT = 600
WIDTH = 800


def rotate(surface, angle, pivot, offset):
    rotated_surface = pygame.transform.rotate(surface, angle)
    rotated_offset = Vector2(offset).rotate(-angle)
    rect = rotated_surface.get_rect(center=pivot + rotated_offset)
    return rotated_surface, rect


class Building(Rect):
    MAX_HEIGHT = 320
    MIN_HEIGHT = 20
    SKINS = [pygame.image.load(f"images/building{i}.png") for i in range(1, 4)]
    WIDTH = 80
    TILE_HEIGHT = 20

    def __init__(self, *args, **kwargs) -> None:
        self.skin = Building.SKINS[kwargs.pop("skin", 0)]
        super().__init__(*args, **kwargs)

    @classmethod
    def random_list(cls, num_buildings: int) -> list["Building"]:
        buildings = []
        for x in range(num_buildings):
            height = random.randint(Building.MIN_HEIGHT, Building.MAX_HEIGHT)
            buildings.append(
                Building(
                    (x * Building.WIDTH, HEIGHT - height),
                    (Building.WIDTH, height),
                    skin=random.randint(0, 2),
                )
            )
        return buildings

    def do_draw(self, surface) -> None:
        for y in range(self.y, self.y + self.height, Building.TILE_HEIGHT):
            surface.blit(self.skin, (self.x, y))


class Skyline:
    def __init__(self):
        self.buildings = []
        self.mask = None
        self.rect = Rect((0, 0), (WIDTH, HEIGHT))
        self.surface = None
        self.num_buildings = 10
        self.generate_buildings()

    def generate_buildings(self):
        self.buildings = Building.random_list(self.num_buildings)
        self.surface = Surface((WIDTH, HEIGHT))
        for building in self.buildings:
            building.do_draw(self.surface)
        self.mask = pygame.mask.from_surface(self.surface)

    def draw(self):
        screen.blit(
            self.mask.to_surface(
                unsetcolor=None,
                setsurface=self.surface,
            ),
            (0, 0),
        )

    def destroy(self, other):
        self.mask.erase(other.mask, (int(other.rect.left), int(other.rect.top)))


class PixelCollision:
    @property
    def mask(self):
        return pygame.mask.from_surface(self._surf)

    @property
    def rect(self):
        return Rect(self.topleft, (self.width, self.height))

    def collided(self, other):
        if not self.rect.colliderect(other.rect):
            return False

        offset = (
            self.rect.left - other.rect.left,
            self.rect.top - other.rect.top,
        )
        return other.mask.overlap(self.mask, offset)


class Gorilla(Actor, PixelCollision):
    HEIGHT = 64
    WIDTH = 64

    def __init__(self, pos: tuple[float, float]) -> None:
        super().__init__("gorilla", pos)


class Explosion:
    HEIGHT = 32
    WIDTH = 32

    def __init__(self, pos: tuple[float, float]) -> None:
        self.rect = Rect(pos, (self.WIDTH, self.HEIGHT))
        self.surface = Surface((self.WIDTH, self.HEIGHT))
        pygame.draw.circle(
            self.surface,
            Color(255, 255, 255),
            (self.WIDTH / 2, self.HEIGHT / 2),
            self.WIDTH / 2,
            width=0,
        )
        self.mask = pygame.mask.from_surface(self.surface)


class Banana(Actor, PixelCollision):
    def __init__(self, pos: tuple[float, float], vx: float, vy: float) -> None:
        super().__init__("banana", pos)
        self.vx = vx
        self.vy = vy

    def explode(self):
        return Explosion((self.x - 16, self.y - 16))

    def draw(self):
        super().draw()


class WindGauge:
    def __init__(self, centertop, dimensions, max_wind_speed) -> None:
        self.indicator = pygame.image.load("images/wind_indicator.png")
        (self.center, self.top) = centertop
        (self.width, self.height) = dimensions
        self.left = self.center - (self.width / 2)
        self.cliprect = Rect((self.width / 2, 0), (0, self.height))
        self.offset = 0
        self.step = (self.width / 2) / max_wind_speed

    def draw(self):
        screen.draw.rect(
            Rect((self.left - 1, self.top), (self.width + 2, self.height + 2)),
            Color(255, 255, 255),
        )
        screen.surface.blit(
            self.indicator,
            (self.center + self.offset, self.top + 1),
            self.cliprect,
        )
        screen.draw.line(
            (self.center, self.top),
            (self.center, self.top + self.height),
            Color(255, 255, 255),
        )

    def set_speed_and_direction(self, speed, direction):
        self.offset = 0
        self.cliprect.left = self.width / 2
        self.cliprect.width = speed * self.step
        if direction < 0:
            self.cliprect.left -= self.cliprect.width
            self.offset = -self.cliprect.width


class HealthBar:
    def __init__(self, pos, size, max_value, flip=False) -> None:
        self.rect = Rect(pos, size)
        self.max_value = max_value
        self.value = max_value
        self.gradient = Gradient(Color(255, 0, 0), Color(255, 255, 0))
        self.surface = self.gradient.get_surface(size, horizontal=True)
        self.flip = flip
        if flip:
            self.surface = pygame.transform.flip(self.surface, True, False)

    @property
    def cliprect(self):
        width = self.rect.width * (self.value / self.max_value)
        x = self.rect.width - width if self.flip else 0
        return Rect(x, 0, width, self.rect.height)

    def draw(self):
        cliprect = self.cliprect
        x = self.rect.width - cliprect.width if self.flip else 0
        screen.surface.blit(
            self.surface, (self.rect.left + x, self.rect.top), self.cliprect
        )


class Scoreboard:
    def __init__(self):
        self.scores = [0, 0]
        self.healthbars = [
            HealthBar((0, 16), (200, 32), 3),
            HealthBar((WIDTH - 200, 16), (200, 32), 3, flip=True),
        ]

    def __iter__(self):
        return iter(self.scores)

    def draw(self):
        for healthbar in self.healthbars:
            healthbar.draw()

    def add_score(self, index, value=1):
        self.scores[index] += value
        self.healthbars[(index + 1) % 2].value -= 1

    def reset(self):
        self.scores = [0, 0]
        for healthbar in self.healthbars:
            healthbar.value = 3


class Hotseat:
    def __init__(self, num_players=2):
        self.index = 0
        self.num_players = num_players

    def draw(self):
        indicator = "p1_indicator.png"
        indicator_pos = 100
        if self.index == 1:
            indicator = "p2_indicator.png"
            indicator_pos = WIDTH - 132
        screen.blit(indicator, (indicator_pos, HEIGHT - 16))

    def next_player(self, *_):
        self.index = (self.index + 1) % self.num_players

    def reset(self):
        self.index = 0


class World:
    def __init__(self):
        self.angle: float = 0
        self.power: int = 0
        self.speed_fudge = 2  # speed up simulation
        self.gravity = 9.8
        self.wind_speed = 0
        self.wind_speed_max = 8
        self.wind_direction = 1
        self.wind_gauge = WindGauge(
            (WIDTH / 2, HEIGHT - 16),
            (160, 14),
            self.wind_speed_max,
        )
        self.gorillas = []
        self.skyline = Skyline()
        self.scoreboard = Scoreboard()
        self.hotseat = Hotseat()
        self.sky = Sky(WIDTH, HEIGHT)
        self.reset()

    def reset(self):
        self.angle = 0
        self.power = 0
        self.hotseat.reset()
        self.scoreboard.reset()
        self.rebuild()

    def rebuild(self, *_):
        self.skyline.generate_buildings()
        self.gorillas = [
            Gorilla(
                (
                    self.skyline.buildings[i].x + Building.WIDTH / 2,
                    self.skyline.buildings[i].y - Gorilla.HEIGHT / 2 + 1,
                )
            )
            for i in (0, self.skyline.num_buildings - 1)
        ]

    def draw(self) -> None:
        screen.blit(self.sky.surface, (0, 0))
        self.skyline.draw()

        for gorilla in self.gorillas:
            gorilla.draw()

        self.scoreboard.draw()
        self.wind_gauge.draw()
        self.hotseat.draw()

    def set_angle_and_power(self, angle, power):
        self.angle = angle
        self.power = power

    def change_wind(self, *_):
        self.wind_speed = random.randint(0, self.wind_speed_max)
        self.wind_direction = random.choice([1, -1])
        self.wind_gauge.set_speed_and_direction(
            self.wind_speed,
            self.wind_direction,
        )

    def set_time(self, *_, time=None):
        if time is None:
            time = random.randint(0, 240)
        self.sky.time = (time % 240) / 10


class GameState(EventSource, State):
    def draw(self) -> None:
        pass

    def update(self, _) -> None:
        pass

    def on_key_up(self, *_) -> None:
        pass

    def on_mouse_down(self, *_) -> None:
        pass

    def on_mouse_move(self, *_) -> None:
        pass

    def on_mouse_up(self, *_) -> None:
        pass


class MainMenu(GameState):
    def __init__(self) -> None:
        self.done = Event()
        self.background = pygame.image.load("images/menu.png")

    def draw(self) -> None:
        screen.blit(self.background, (0, 0))

    def on_key_up(self, *_) -> None:
        self.done()


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

        self.on_done(self.world.draw)
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

    def draw(self) -> None:
        self.world.draw()
        screen.draw.filled_rect(
            Rect(self.bar_pos.at(self.timer), self.bar_size.at(self.timer)),
            Color(255, 0, 255),
        )
        screen.blit(
            self.get_ready[self.world.hotseat.index],
            self.text_pos.at(self.timer),
        )

    def update(self, dt) -> None:
        if not hasattr(self, "timer"):
            self.timer = 0
        self.timer += dt
        if self.timer > 3:
            self.done()
            self.timer = 0


class ThrowInput(GameState):
    RETICLE_WIDTH = 32

    def __init__(self, world) -> None:
        self.change_per_second = 100
        self.direction = 1
        self.done = Event()
        self.angle_input = 0
        self.power_input = 10
        self.min_power = 10
        self.max_power = 200
        self.pulse_power = False
        self.reticle = pygame.image.load("images/reticle.png")
        self.powerbar = pygame.image.load("images/powerbar.png")
        self.world = world

    def draw(self) -> None:
        self.world.draw()

        gorilla = self.world.gorillas[self.world.hotseat.index]
        angle = int(self.angle_input * (180 / math.pi))
        if self.world.hotseat.index == 1:
            angle = 180 - angle
        power = int(self.power_input)

        screen.draw.filled_rect(Rect((0, 0), (WIDTH, 16)), Color(0, 0, 0))
        screen.draw.text(
            f"Angle: {str(angle)}, Power: {str(power)}",
            (0, 0),
        )

        angle_x = math.cos(self.angle_input)
        angle_y = math.sin(self.angle_input)

        reticle_pos = (
            gorilla.x + angle_x * Gorilla.WIDTH - self.RETICLE_WIDTH / 2,
            gorilla.y - angle_y * Gorilla.WIDTH - self.RETICLE_WIDTH / 2,
        )
        screen.blit(self.reticle, reticle_pos)

        if self.pulse_power:
            half_width = Gorilla.WIDTH / 2
            powerbar_length = (self.power_input / self.max_power) * half_width
            powerbar = self.powerbar.subsurface(
                Rect((0, 0), (half_width + powerbar_length, Gorilla.HEIGHT)),
            ).copy()
            powerbar, rect = rotate(
                powerbar,
                int(self.angle_input * (180 / math.pi)),
                gorilla.center,
                (powerbar_length / 2 + 16, 0),
            )
            screen.blit(
                powerbar,
                rect.topleft,
            )

    def update(self, dt) -> None:
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
        gorilla = self.world.gorillas[self.world.hotseat.index]
        self.angle_input = math.atan2(gorilla.y - y, x - gorilla.x)

    def reset_angle(self, *_):
        self.set_angle_from_mouse_pos(pygame.mouse.get_pos())

    def on_mouse_move(self, pos, rel, buttons):
        self.set_angle_from_mouse_pos(pos)

    def on_mouse_down(self, pos, button):
        self.pulse_power = True
        self.power_input = self.min_power

    def on_mouse_up(self, pos, button):
        self.pulse_power = False
        self.done(self.angle_input, self.power_input)


class Throw(GameState):
    def __init__(self, world: World) -> None:
        self.done = Event()
        self.hit_gorilla = Event()
        self.world = world
        self.banana = None
        self.opponent = None

        self.on_done(self.reset)

    def reset(self):
        self.banana = None
        self.opponent = None

    def draw(self) -> None:
        self.world.draw()
        if self.banana:
            self.banana.draw()

    def update(self, dt) -> None:
        if not self.banana:
            self.launch_banana()

        self.banana.angle += 5
        self.banana.x += dt * self.world.speed_fudge * self.banana.vx
        self.banana.y += dt * self.world.speed_fudge * self.banana.vy

        self.banana.vx += (
            dt
            * self.world.speed_fudge
            * self.world.wind_direction
            * self.world.wind_speed
        )
        self.banana.vy += dt * self.world.speed_fudge * self.world.gravity

        if self.banana.x < 0 or self.banana.x > WIDTH or self.banana.y > HEIGHT:
            return self.done()

        if self.banana.collided(self.opponent):
            self.hit_gorilla(self.world.hotseat.index)
            sounds.hit.play()
            return self.done()

        if self.banana.collided(self.world.skyline):
            self.world.skyline.destroy(self.banana.explode())
            sounds.hit.play()
            return self.done()

    def launch_banana(self) -> None:
        gorilla = self.world.gorillas[self.world.hotseat.index]
        self.opponent = self.world.gorillas[(self.world.hotseat.index + 1) % 2]
        self.banana = Banana(
            (gorilla.x, gorilla.y),
            vx=self.world.power * math.cos(self.world.angle),
            vy=-1 * self.world.power * math.sin(self.world.angle),
        )
        sounds.throw.play()


class GameOver(GameState):
    def __init__(self) -> None:
        self.done = Event()

    def draw(self) -> None:
        screen.clear()
        screen.draw.text("GAME OVER", (WIDTH / 2 - 50, HEIGHT / 2))

    def on_key_up(self, *_) -> None:
        self.done()


class Game(StateMachine):
    def __init__(self) -> None:
        self.world = World()

        menu = MainMenu()
        get_ready = GetReady(self.world)
        throw_input = ThrowInput(self.world)
        throw = Throw(self.world)
        game_over = GameOver()

        menu.on_done(self.transition(get_ready))
        get_ready.on_done(self.transition(throw_input))
        get_ready.on_done(throw_input.reset_angle)
        throw_input.on_done(self.world.set_angle_and_power)
        throw_input.on_done(self.transition(throw))
        throw.on_hit_gorilla(self.world.scoreboard.add_score)
        throw.on_hit_gorilla(self.world.change_wind)
        throw.on_hit_gorilla(self.world.set_time)
        throw.on_hit_gorilla(self.world.rebuild)
        throw.on_done(self.transition(game_over, condition=self.done))
        throw.on_done(self.world.hotseat.next_player)
        throw.on_done(self.transition(get_ready, condition=lambda: not self.done()))
        game_over.on_done(self.world.reset)
        game_over.on_done(self.transition(menu))

        self.current_state = menu

    def done(self) -> bool:
        return any(score > 2 for score in self.world.scoreboard)

    def draw(self) -> None:
        self.current_state.draw()

    def update(self, dt) -> None:
        self.current_state.update(dt)

    def on_key_up(self, *args, **kwargs) -> None:
        if args[0] == keys.T:
            self.world.set_time()
        if args[0] == keys.W:
            self.world.change_wind()
        if args[0] == keys.R:
            self.world.reset()
        self.current_state.on_key_up(*args, **kwargs)

    def on_mouse_down(self, *args, **kwargs) -> None:
        self.current_state.on_mouse_down(*args, **kwargs)

    def on_mouse_move(self, *args, **kwargs) -> None:
        self.current_state.on_mouse_move(*args, **kwargs)

    def on_mouse_up(self, *args, **kwargs) -> None:
        self.current_state.on_mouse_up(*args, **kwargs)


game = Game()


def draw() -> None:
    game.draw()


def update(dt) -> None:
    game.update(dt)


def on_key_up(key, mod) -> None:
    game.on_key_up(key, mod)


def on_mouse_down(pos, button) -> None:
    game.on_mouse_down(pos, button)


def on_mouse_move(pos, rel, buttons) -> None:
    game.on_mouse_move(pos, rel, buttons)


def on_mouse_up(pos, button) -> None:
    game.on_mouse_up(pos, button)
