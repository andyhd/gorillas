import math
import random

import pygame
from pgzero.actor import Actor
from pgzero.keyboard import keys
from pgzero.rect import Rect

from event import Event
from event import EventSource
from state import State
from state import StateMachine


HEIGHT = 600
WIDTH = 800


class Building(Rect):
    MAX_HEIGHT = 320
    MIN_HEIGHT = 20
    SKINS = [
        pygame.image.load(f"images/building{i}.png")
        for i in range(1, 4)
    ]
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
            buildings.append(Building(
                (x * Building.WIDTH, HEIGHT - height), (Building.WIDTH, height),
                skin=random.randint(0, 2),
            ))
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
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        for building in self.buildings:
            building.do_draw(self.surface)
        self.mask = pygame.mask.from_surface(self.surface)

    def draw(self):
        screen.blit(self.mask.to_surface(
            unsetcolor=None,
            setsurface=self.surface,
        ), (0, 0))

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
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        pygame.draw.circle(
            self.surface,
            "white",
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
            "white",
        )
        screen.surface.blit(
            self.indicator,
            (self.center + self.offset, self.top + 1),
            self.cliprect,
        )
        screen.draw.line(
            (self.center, self.top),
            (self.center, self.top + self.height),
            "white",
        )

    def set_speed_and_direction(self, speed, direction):
        self.offset = 0
        self.cliprect.left = self.width / 2
        self.cliprect.width = speed * self.step
        if direction < 0:
            self.cliprect.left -= self.cliprect.width
            self.offset = -self.cliprect.width


class Scoreboard:
    def __init__(self):
        self.scores = [0, 0]

    def __iter__(self):
        return iter(self.scores)

    def draw(self):
        screen.draw.filled_rect(Rect((0, HEIGHT - 16), (WIDTH, 16)), (0, 0, 0))
        screen.draw.text(f"Player 1: {self.scores[0]}", (0, HEIGHT - 16))
        screen.draw.text(f"Player 2: {self.scores[1]}", (WIDTH - 90, HEIGHT - 16))

    def add_score(self, index, value=1):
        self.scores[index] += value

    def reset(self):
        self.scores = [0, 0]


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
        self.speed: int = 0
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
        self.sky = pygame.image.load("images/sky.png")
        self.reset()

    def reset(self):
        self.angle = 0
        self.speed = 0
        self.hotseat.reset()
        self.scoreboard.reset()
        self.rebuild()

    def rebuild(self, *_):
        self.skyline.generate_buildings()
        self.gorillas = [
            Gorilla((
                self.skyline.buildings[i].x + Building.WIDTH / 2,
                self.skyline.buildings[i].y - Gorilla.HEIGHT / 2 + 1,
            ))
            for i in (0, self.skyline.num_buildings - 1)
        ]

    def draw(self) -> None:
        screen.blit(self.sky, (0, 0))

        self.skyline.draw()

        for gorilla in self.gorillas:
            gorilla.draw()

        self.scoreboard.draw()
        self.wind_gauge.draw()
        self.hotseat.draw()

    def set_angle(self, angle):
        self.angle = math.radians(int(angle))

    def set_speed(self, speed):
        self.speed = int(speed)

    def change_wind(self, *_):
        self.wind_speed = random.randint(0, self.wind_speed_max)
        self.wind_direction = random.choice([1, -1])
        self.wind_gauge.set_speed_and_direction(
            self.wind_speed,
            self.wind_direction,
        )


class GameState(EventSource, State):
    def draw(self) -> None:
        pass

    def update(self, _) -> None:
        pass

    def on_key_up(self, *_) -> None:
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

        self.on_done(self.world.draw)

    def draw(self) -> None:
        self.world.draw()
        screen.draw.filled_rect(Rect((0, HEIGHT / 2), (WIDTH, 16)), (0, 0, 0))
        screen.draw.text(f"Get ready Player {self.world.hotseat.index + 1}", (WIDTH / 2 - 90, HEIGHT / 2))

    def update(self, dt) -> None:
        if not hasattr(self, "timer"):
            self.timer = 0
        self.timer += dt
        if self.timer > 3:
            self.done()
            self.timer = 0


class NumberInput(GameState):
    def __init__(self, prompt: str) -> None:
        self.done = Event()
        self.input: list[str] = []
        self.prompt = prompt

    def draw(self) -> None:
        screen.draw.filled_rect(Rect((0, 0), (WIDTH, 16)), (0, 0, 0))
        screen.draw.text(
            f"{self.prompt}: {''.join(self.input)}",
            (0, 0),
        )

    def on_key_up(self, key: int, *_) -> None:
        number_keys = [getattr(keys, f"K_{i}") for i in range(10)]

        for i, number_key in enumerate(number_keys):
            if key == number_key:
                self.input.append(str(i))

        if key == keys.BACKSPACE and len(self.input):
            self.input.pop()

        if key == keys.RETURN:
            self.done("".join(self.input))
            self.input = []


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
        self.banana.x += (dt * self.world.speed_fudge * self.banana.vx)
        self.banana.y += (dt * self.world.speed_fudge * self.banana.vy)

        self.banana.vx += dt * self.world.speed_fudge * self.world.wind_direction * self.world.wind_speed
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
            (gorilla.x, gorilla.y - Gorilla.HEIGHT / 2),
            vx=self.world.speed * math.cos(self.world.angle),
            vy=-1 * self.world.speed * math.sin(self.world.angle),
        )
        if self.world.hotseat.index == 1:
            self.banana.vx = -self.banana.vx
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
        angle_input = NumberInput("Angle")
        speed_input = NumberInput("Speed")
        throw = Throw(self.world)
        game_over = GameOver()

        menu.on_done(self.transition(get_ready))
        get_ready.on_done(self.transition(angle_input))
        angle_input.on_done(self.world.set_angle)
        angle_input.on_done(self.transition(speed_input))
        speed_input.on_done(self.world.set_speed)
        speed_input.on_done(self.transition(throw))
        throw.on_hit_gorilla(self.world.scoreboard.add_score)
        throw.on_hit_gorilla(self.world.change_wind)
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
        self.current_state.on_key_up(*args, **kwargs)


game = Game()


def draw() -> None:
    game.draw()


def update(dt) -> None:
    game.update(dt)


def on_key_up(key, mod) -> None:
    game.on_key_up(key, mod)
