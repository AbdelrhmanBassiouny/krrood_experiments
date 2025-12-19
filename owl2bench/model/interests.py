from dataclasses import dataclass

from .base import Interest


@dataclass
class Game(Interest): ...


@dataclass
class Movie(Interest): ...


@dataclass
class Music(Interest): ...


@dataclass
class Painting(Interest): ...


@dataclass
class Reading(Interest): ...


@dataclass
class Travelling(Interest): ...


@dataclass
class Sports(Interest): ...


@dataclass
class Badminton(Sports): ...


@dataclass
class BasketBall(Sports): ...


@dataclass
class Cricket(Sports): ...


@dataclass
class FootBall(Sports): ...


@dataclass
class Swimming(Sports): ...


@dataclass
class Tennis(Sports): ...
