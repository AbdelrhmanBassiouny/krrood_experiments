from dataclasses import dataclass

from .base import Program


@dataclass(eq=False)
class UndergraduateProgram(Program): ...


@dataclass(eq=False)
class PostgraduateProgram(Program): ...


@dataclass(eq=False)
class PhDProgram(Program): ...
