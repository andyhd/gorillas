import math
import random

import pygame
from pgzero.actor import Actor
from pgzero.keyboard import keys
from pgzero.rect import Rect
from pygame.sprite import collide_mask

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
        for y in range(self.y, self.y + self.height, 20):
            surface.blit(self.skin, (self.x, y))


class PixelCollision:

    @property
    def mask(self):
        return pygame.mask.from_surface(self._surf)

    @property
    def rect(self):
        return Rect(self.topleft, (self.width, self.height))

    def collided(self, other):
        return collide_mask(self, other)


class Gorilla(Actor, PixelCollision):
    HEIGHT = 64
    WIDTH = 64

    def __init__(self, pos: tuple[float, float]) -> None:
        super().__init__("gorilla", pos)


class Banana(Actor, PixelCollision):
    def __init__(self, pos: tuple[float, float], vx: float, vy: float) -> None:
        super().__init__("banana", pos)
        self.vx = vx
        self.vy = vy


class World:
    def __init__(self):
        self.angle: float = 0
        self.speed: int = 0
        self.speed_fudge = 2  # speed up simulation
        self.gravity = 9.8
        self.wind_speed = 0
        self.wind_direction = 1
        self.buildings = []
        self.buildings_mask = None
        self.buildings_surf = None
        self.gorillas = []
        self.scores = []
        self.num_buildings = 10
        self.sky = pygame.image.load("images/sky.png")
        self.explosion = pygame.Surface((32, 32))
        pygame.draw.circle(self.explosion, "white", (16, 16), 16, width=0)
        self.explosion_mask = pygame.mask.from_surface(self.explosion)
        self.reset()

    def reset(self):
        self.angle = 0
        self.speed = 0
        self.hotseat = 0
        self.scores = [0, 0]
        self.rebuild()

    def rebuild(self, *_):
        self.buildings = Building.random_list(self.num_buildings)
        self.buildings_surf = pygame.Surface((WIDTH, HEIGHT))
        for building in self.buildings:
            building.do_draw(self.buildings_surf)
        self.buildings_mask = pygame.mask.from_surface(self.buildings_surf)
        self.gorillas = [
            Gorilla((
                self.buildings[i].x + Building.WIDTH / 2,
                self.buildings[i].y - Gorilla.HEIGHT / 2 + 1,
            ))
            for i in (0, self.num_buildings - 1)
        ]

    def draw(self) -> None:
        screen.blit(self.sky, (0, 0))

        screen.blit(self.buildings_mask.to_surface(
            unsetcolor=None,
            setsurface=self.buildings_surf,
        ), (0, 0))

        for gorilla in self.gorillas:
            gorilla.draw()

        screen.draw.filled_rect(Rect((0, HEIGHT - 16), (WIDTH, 16)), (0, 0, 0))
        screen.draw.text(f"Player 1: {self.scores[0]}", (0, HEIGHT - 16))
        screen.draw.text(f"Player 2: {self.scores[1]}", (WIDTH - 90, HEIGHT - 16))

        screen.draw.rect(
            Rect(
                (WIDTH / 2 - 81, HEIGHT - 16),
                (162, 16),
            ),
            (255, 255, 255),
        )
        bar = Rect((0, HEIGHT - 15), (self.wind_speed * 8, 14))
        if self.wind_direction > 0:
            bar.x = WIDTH / 2
        else:
            bar.x = WIDTH / 2 - self.wind_speed * 8
        screen.draw.filled_rect(bar, (255, 0, 0))
        screen.draw.line((WIDTH / 2, HEIGHT - 16), (WIDTH / 2, HEIGHT), (255, 255, 255))

    def set_angle(self, angle):
        self.angle = math.radians(int(angle))

    def set_speed(self, speed):
        self.speed = int(speed)

    def update_score(self, gorilla_hit):
        self.scores[(gorilla_hit + 1) % 2] += 1

    def toggle_hotseat(self):
        self.hotseat = (self.hotseat + 1) % 2

    def change_wind(self, *_):
        self.wind_speed = random.randint(0, 10)
        self.wind_direction = random.choice([1, -1])


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
        screen.draw.text(f"Get ready Player {self.world.hotseat + 1}", (WIDTH / 2 - 90, HEIGHT / 2))

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
        self.on_hit_gorilla(sounds.hit.play)

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
            self.done()

        elif self.banana.collided(self.opponent):
            self.hit_gorilla((self.world.hotseat + 1) % 2)
            self.done()

        elif self.world.buildings_mask.overlap(
            self.banana.mask,
            (int(self.banana.left), int(self.banana.top)),
        ):
            self.world.buildings_mask.erase(
                self.world.explosion_mask,
                (int(self.banana.x - 16), int(self.banana.y - 16)),
            )
            sounds.hit.play()
            self.done()

    def launch_banana(self) -> None:
        gorilla = self.world.gorillas[self.world.hotseat]
        self.opponent = self.world.gorillas[(self.world.hotseat + 1) % 2]
        self.banana = Banana(
            (gorilla.x, gorilla.y - Gorilla.HEIGHT / 2),
            vx=self.world.speed * math.cos(self.world.angle),
            vy=-1 * self.world.speed * math.sin(self.world.angle),
        )
        if self.world.hotseat == 1:
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
        throw.on_hit_gorilla(self.world.update_score)
        throw.on_hit_gorilla(self.world.change_wind)
        throw.on_hit_gorilla(self.world.rebuild)
        throw.on_done(self.transition(game_over, condition=self.done))
        throw.on_done(self.world.toggle_hotseat)
        throw.on_done(self.transition(get_ready, condition=lambda: not self.done()))
        game_over.on_done(self.world.reset)
        game_over.on_done(self.transition(menu))

        self.current_state = menu

    def done(self) -> bool:
        return any(score > 2 for score in self.world.scores)

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
