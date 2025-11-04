from dataclasses import dataclass
from typing import Tuple


class ConfigurationError(Exception):
    """Raised when an invalid configuration is provided."""


@dataclass(frozen=True)
class Range:
    """
    A closed integer range.

    :param minimum: Inclusive lower bound
    :param maximum: Inclusive upper bound
    """
    minimum: int
    maximum: int

    def __post_init__(self) -> None:
        if self.minimum < 0 or self.maximum < 0:
            raise ConfigurationError("Range values must be non-negative integers.")
        if self.maximum < self.minimum:
            raise ConfigurationError("Range maximum must be greater than or equal to minimum.")

    def as_tuple(self) -> Tuple[int, int]:
        return self.minimum, self.maximum


@dataclass(frozen=True)
class InstanceConfig:
    """
    Configuration for generating an OWL2Bench-like instance graph.

    All counts are inclusive integer ranges. Only a representative subset
    of the original Java Generator parameters is modeled to keep the
    Python package small but useful.

    :param colleges: Number of colleges per university
    :param departments: Number of departments per college
    :param undergraduate_students: Number of undergraduate students per department
    :param postgraduate_students: Number of postgraduate students per department
    :param phd_students: Number of PhD students per department
    :param courses: Number of courses per department
    :param women_college_ratio: Probability that a college is women-only (0..1)
    """

    colleges: Range = Range(2, 4)
    departments: Range = Range(2, 3)
    undergraduate_students: Range = Range(5, 10)
    postgraduate_students: Range = Range(2, 5)
    phd_students: Range = Range(1, 3)
    courses: Range = Range(3, 6)
    women_college_ratio: float = 0.2

    def __post_init__(self) -> None:  # type: ignore[override]
        if not (0.0 <= self.women_college_ratio <= 1.0):
            raise ConfigurationError("women_college_ratio must be between 0 and 1 (inclusive).")
