from dataclasses import dataclass

from .base import Program


@dataclass
class UndergraduateProgram(Program): ...


@dataclass
class PostgraduateProgram(Program): ...


@dataclass
class PhDProgram(Program): ...
