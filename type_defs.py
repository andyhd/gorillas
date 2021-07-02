from typing import Callable
from typing import Iterable
from typing import Union

from pygame.math import Vector2


Vector = Union[Iterable[float], tuple[float, float], Vector2]
Size = Vector
Translation = Callable[[Vector], Vector]
