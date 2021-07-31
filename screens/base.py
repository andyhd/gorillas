from typing import Optional

from pygame import Rect
from pygame import Surface

import config
from event import Event
from event import EventSource
from state import Callback
from state import Condition
from state import State
from state import StateMachine


class Screen(EventSource, State):
    def __init__(self) -> None:
        self.enter = Event()
        self.exit = Event()
        self.rect = Rect(0, 0, config.WIDTH, config.HEIGHT)
        self.surface = Surface(self.rect.size).convert_alpha()

    def render(self, surface: Surface) -> None:
        surface.blit(self.surface, self.rect.topleft)

    def update(self, _: float) -> None:
        pass

    def on_key_up(self, *_) -> None:
        pass

    def on_mouse_down(self, *_) -> None:
        pass

    def on_mouse_move(self, *_) -> None:
        pass

    def on_mouse_up(self, *_) -> None:
        pass


class ScreenManager(StateMachine):
    def set_state(
        self,
        to_state: State,
        condition: Condition = True,
        transition=None,
    ) -> Callback:
        do_set_state = super().set_state(to_state)

        def state_setter(*_) -> None:
            if not condition or callable(condition) and not condition():
                return

            self._transition = None

            if transition:
                self._transition = transition
                self.transition.from_screen = self.current_state
                self.transition.to_screen = to_state
                self.transition.on_exit(self.clear_transition)
                self.transition.on_exit(do_set_state)

            else:
                self.current_state = to_state

        return state_setter

    def render(self, surface: Surface) -> None:
        if self.transition:
            self.transition.render(surface)
        else:
            self.current_state.render(surface)

    def update(self, dt: float) -> None:
        if self.transition:
            self.transition.update(dt)

        else:
            self.current_state.update(dt)

    @property
    def transition(self):
        if not hasattr(self, "_transition"):
            self._transition = None

        return self._transition

    def clear_transition(self, *_):
        self._transition = None
