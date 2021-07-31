from pygame import K_r
from pygame import K_t
from pygame import K_w

from screens import GameOver
from screens import GetReady
from screens import MainMenu
from screens import Throw
from screens import ThrowInput
from screens.base import ScreenManager
from transition import FadeToBlack
from transition import Wipe
from world import World


class Game(ScreenManager):
    def __init__(self) -> None:
        self.world = World()

        menu = MainMenu()
        get_ready = GetReady(self.world)
        throw_input = ThrowInput(self.world)
        throw = Throw(self.world)
        game_over = GameOver()

        menu.on_exit(
            self.set_state(
                get_ready,
                transition=Wipe(0.3),
            )
        )
        get_ready.on_exit(self.set_state(throw_input))
        get_ready.on_exit(throw_input.reset_angle)
        throw_input.on_exit(self.world.set_angle_and_power)
        throw_input.on_exit(self.set_state(throw))
        throw.on_hit_gorilla(self.world.scoreboard.add_score)
        throw.on_hit_gorilla(self.world.change_wind)
        throw.on_hit_gorilla(self.world.set_time)
        throw.on_hit_gorilla(self.world.rebuild)
        throw.on_exit(
            self.set_state(
                game_over,
                condition=self.done,
                transition=FadeToBlack(3),
            ),
        )
        throw.on_exit(self.world.next_player)
        throw.on_exit(self.set_state(get_ready, condition=lambda: not self.done()))
        game_over.on_exit(self.world.reset)
        game_over.on_exit(self.set_state(menu))

        self.current_state = menu

    def done(self) -> bool:
        return any(score > 2 for score in self.world.scoreboard)

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
