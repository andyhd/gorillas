from typing import Callable
from typing import Union


Callback = Callable[[], None]
Condition = Union[bool, Callable[[], bool]]


class State:
    def enter(self) -> None:
        pass

    def exit(self, *_) -> None:
        pass


class StateMachine:
    @property
    def current_state(self) -> State:
        if not hasattr(self, "_current_state"):
            raise AttributeError("No current state")
        return self._current_state

    @current_state.setter
    def current_state(self, state: State) -> None:
        self._current_state = state
        self._current_state.enter()

    def set_state(
        self,
        to_state: State,
        condition: Condition = True,
    ) -> Callback:
        def state_setter(*_) -> None:
            if (callable(condition) and condition()) or condition:
                self.current_state = to_state

        return state_setter
