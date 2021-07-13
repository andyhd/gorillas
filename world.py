import random

from pygame import Rect
from pygame.math import Vector2

from config import HEIGHT
from config import WIDTH
from explosion import Explosion
from explosion import ExplosionEmitter
from gorilla import Gorilla
from particle import Emitter
from sky import clouds
from sky import make_cloud_particle
from sky import Sky
from terrain import Building
from terrain import Skyline
from ui import HotseatIndicator
from ui import Scoreboard
from ui import WindGauge
from wind import debris
from wind import Wind


class World:
    def __init__(self):
        self.angle: float = 0
        self.power: int = 0
        self.gravity = 9.8
        self.current_player = 0
        self.wind = Wind(max_speed=8)
        self.wind_gauge = WindGauge(
            (WIDTH / 2 - 80, HEIGHT - 16),
            (160, 16),
            self.wind,
        )
        self.gorillas = []
        self.skyline = Skyline()
        self.scoreboard = Scoreboard()
        self.hotseat = HotseatIndicator()
        self.sky = Sky(WIDTH, HEIGHT)
        bounds = Rect(-150, 0, WIDTH + 300, HEIGHT)
        self.emitters = []
        cloud_emitter = Emitter(max_particles=7)
        cloud_emitter.add_stream(
            clouds(self.wind, bounds),
        )
        for _ in range(7):
            cloud = make_cloud_particle(self.wind, bounds)
            cloud.pos.x = random.randrange(WIDTH)
            cloud.pos.y = random.randrange(60, int(bounds.height / 4))
            cloud_emitter.particles.append(cloud)
        self.emitters.append(cloud_emitter)
        wind_debris = Emitter()
        wind_debris.add_stream(debris(self.wind, bounds))
        self.emitters.append(wind_debris)
        self.reset()

    def reset(self):
        self.angle = 0
        self.power = 0
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
        self.hotseat.pos = Vector2(
            self.gorillas[0].rect.left, self.gorillas[0].rect.top - 128
        )

    def update(self, dt) -> None:
        self.hotseat.update(dt)
        for emitter in self.emitters:
            emitter.update(dt)

    def render(self, surface) -> None:
        surface.blit(self.sky.surface, (0, 0))
        self.skyline.render(surface)
        for emitter in self.emitters:
            emitter.render(surface)

        for gorilla in self.gorillas:
            gorilla.render(surface)

        self.scoreboard.render(surface)
        self.wind_gauge.render(surface)
        self.hotseat.render(surface)

    def set_angle_and_power(self, angle, power):
        self.angle = angle
        self.power = power

    def change_wind(self, *_):
        self.wind.change()

    def set_time(self, *_, time=None):
        if time is None:
            time = random.randint(0, 240)
        self.sky.time = (time % 240) / 10

    def add_explosion(self, pos):
        explosion = Explosion(pos)
        self.skyline.destroy(explosion)
        emitter = ExplosionEmitter(pos=pos)
        emitter.on_done(self.remove_explosion)
        self.emitters.append(emitter)

    def remove_explosion(self, emitter):
        def _remove_explosion():
            self.emitters.remove(emitter)

        return _remove_explosion

    def next_player(self, *_):
        self.current_player = (self.current_player + 1) % 2
        self.hotseat.pos = Vector2(
            self.gorillas[self.current_player].rect.left,
            self.gorillas[self.current_player].rect.top - 128,
        )
