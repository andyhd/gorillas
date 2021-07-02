from event import EventSource
from state import State


class GameState(EventSource, State):
    def render(self, surface) -> None:
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
