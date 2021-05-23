from typing import Any
from typing import Callable
from typing import Optional


class State:
    def set_context(self, context: dict[str, Any]):
        if context:
            self.__dict__.update(context)


class StateMachine:

    @property
    def current_state(self) -> State:
        if not hasattr(self, "_current_state"):
            raise AttributeError("No current state")
        return self._current_state

    @current_state.setter
    def current_state(self, state: State) -> None:
        self._current_state = state

    def transition(
        self,
        to_state: State,
        condition: Optional[Callable[[], bool]] = None,
        **context,
    ) -> Callable[[], None]:
        def state_setter(*args, **kwargs) -> None:
            if callable(condition) and not condition():
                return
            self.current_state = to_state
            self.current_state.set_context(context)
        return state_setter
