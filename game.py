from pygame import K_r
from pygame import K_t
from pygame import K_w

from state import StateMachine
from states import GameOver
from states import GetReady
from states import MainMenu
from states import Throw
from states import ThrowInput
from world import World


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
        throw.on_done(self.world.next_player)
        throw.on_done(self.transition(get_ready, condition=lambda: not self.done()))
        game_over.on_done(self.world.reset)
        game_over.on_done(self.transition(menu))

        self.current_state = menu

    def done(self) -> bool:
        return any(score > 2 for score in self.world.scoreboard)

    def render(self, surface) -> None:
        self.current_state.render(surface)

    def update(self, dt) -> None:
        self.current_state.update(dt)

    def on_key_up(self, *args, **kwargs) -> None:
        if args[0] == K_t:
            self.world.set_time()
        if args[0] == K_w:
            self.world.change_wind()
        if args[0] == K_r:
            self.world.reset()
        self.current_state.on_key_up(*args, **kwargs)

    def on_mouse_down(self, *args, **kwargs) -> None:
        self.current_state.on_mouse_down(*args, **kwargs)

    def on_mouse_move(self, *args, **kwargs) -> None:
        self.current_state.on_mouse_move(*args, **kwargs)

    def on_mouse_up(self, *args, **kwargs) -> None:
        self.current_state.on_mouse_up(*args, **kwargs)
