from dataclasses import dataclass

from .base import Interest


@dataclass(eq=False)
class Game(Interest): ...


@dataclass(eq=False)
class Movie(Interest): ...


@dataclass(eq=False)
class Music(Interest): ...


@dataclass(eq=False)
class Painting(Interest): ...


@dataclass(eq=False)
class Reading(Interest): ...


@dataclass(eq=False)
class Travelling(Interest): ...


@dataclass(eq=False)
class Sports(Interest): ...


@dataclass(eq=False)
class Badminton(Sports): ...


@dataclass(eq=False)
class BasketBall(Sports): ...


@dataclass(eq=False)
class Cricket(Sports): ...


@dataclass(eq=False)
class FootBall(Sports): ...


@dataclass(eq=False)
class Swimming(Sports): ...


@dataclass(eq=False)
class Tennis(Sports): ...
