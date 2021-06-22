from operator import attrgetter
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union


T = TypeVar("T")
Timestamp = Union[int, float]
Lerp = Callable[[T, T, float], T]


def interpolate(start: float, end: float, quotient: float) -> float:
    return start + quotient * (end - start)


class KeyFrame:
    """
    Represents a state at a specific time
    """

    def __init__(self, timestamp: Timestamp, state: Any) -> None:
        self.timestamp = timestamp
        self.state = state


class Timeline:
    """
    Contains a sorted list of KeyFrames
    """

    def __init__(
        self,
        *keyframes: Union[KeyFrame, tuple[Timestamp, Any]],
        lerp: Optional[Lerp] = None,
    ) -> None:
        self.keyframes: list[KeyFrame] = sorted(
            [
                keyframe if isinstance(keyframe, KeyFrame) else KeyFrame(*keyframe)
                for keyframe in keyframes
            ],
            key=attrgetter("timestamp"),
        )
        self.lerp = lerp

    def at(self, timestamp: Timestamp) -> Any:
        """
        Get the animation state at the specified timestamp
        """

        start = self.keyframes[0]
        if timestamp <= start.timestamp:
            return start.state

        end = self.keyframes[-1]
        if timestamp >= end.timestamp:
            return end.state

        for frame in self.keyframes:
            if frame.timestamp <= timestamp:
                start = frame
                continue
            if frame.timestamp >= timestamp:
                end = frame
                break

        duration = end.timestamp - start.timestamp
        progress = (timestamp - start.timestamp) / duration

        lerp = self.lerp
        if not lerp:
            lerp = (
                type(start.state).lerp if hasattr(start.state, "lerp") else interpolate
            )
        return lerp(start.state, end.state, progress)
