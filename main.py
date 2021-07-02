from config import HEIGHT
from config import WIDTH
from game import Game


game = Game()


def draw() -> None:
    game.render(screen.surface)


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
