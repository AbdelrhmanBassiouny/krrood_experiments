from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import logging
import warnings
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

from .models import (
    World,
    University,
    College,
    Department,
    Course,
    Person,
)


class OntologyLoadError(Exception):
    """
    Raised when an OWL/RDF file cannot be parsed.
    """


class MappingError(Exception):
    """
    Raised when required data is missing for constructing model objects.
    """


BENCH = Namespace("http://benchmark/OWL2Bench#")


@dataclass(frozen=True)
class WorldLoader:
    """
    Loads a `World` from an OWL/RDF file using RDFLib.

    The loader extracts a pragmatic subset of OWL2Bench:
    - Universities, Colleges (women-only via class membership), Departments, Courses
    - Persons with first name, last name, email, and gender inferred from Woman/Man classes

    Missing required attributes (first name, last name, email, gender) raise `MappingError`.
    Missing nice-to-have attributes (like course titles) are filled with fallbacks and
    reported via warnings.

    This implementation uses selective triple pattern queries and avoids full-graph
    iteration where possible. The file is parsed into an RDFLib `Graph`.
    """

    def load(self, file_path: str | Path) -> World:
        path = Path(file_path)
        if not path.exists():
            raise OntologyLoadError(f"File not found: {path}")

        try:
            g = Graph()
            # Try to guess format by extension; rdflib can auto-detect for XML/Turtle
            g.parse(path.as_posix())
        except Exception as exc:  # noqa: BLE001 (bubbling into custom exception)
            raise OntologyLoadError(f"Failed to parse RDF from {path}: {exc}") from exc

        # Build lookups progressively
        universities: List[University] = []
        colleges_index: Dict[URIRef, College] = {}
        departments_index: Dict[URIRef, Department] = {}
        courses_index: Dict[URIRef, Course] = {}
        persons_index: Dict[URIRef, Person] = {}

        # Helper to get a human-friendly identifier from an IRI
        def ident(iri: URIRef) -> str:
            s = str(iri)
            return s.rsplit('#', 1)[-1] if '#' in s else s.rstrip('/').rsplit('/', 1)[-1]

        # Universities
        for u in g.subjects(RDF.type, BENCH.University):
            u_id = ident(u)
            u_name = self._label_or_fallback(g, u, default=u_id)
            uni = University(identifier=u_id, name=u_name)

            # Colleges via hasCollege / hasWomenCollege and inverses isCollegeOf / isWomenCollegeOf
            college_nodes = set(g.objects(u, BENCH.hasCollege)) | set(g.objects(u, BENCH.hasWomenCollege))
            # Inverses: find colleges where c is isCollegeOf or isWomenCollegeOf u
            college_nodes |= set(g.subjects(BENCH.isCollegeOf, u))
            college_nodes |= set(g.subjects(BENCH.isWomenCollegeOf, u))
            college_objs: List[College] = []
            for c in college_nodes:
                if not isinstance(c, URIRef):
                    continue
                college = colleges_index.get(c)
                if college is None:
                    c_id = ident(c)
                    c_name = self._label_or_fallback(g, c, default=c_id)
                    # women-only flag via type WomenCollege
                    is_women_only = (c, RDF.type, BENCH.WomenCollege) in g
                    college = College(identifier=c_id, name=c_name, is_women_only=is_women_only)
                    # Departments (hasDepartment) and inverse isDepartmentOf
                    dept_nodes = set(g.objects(c, BENCH.hasDepartment)) | set(g.subjects(BENCH.isDepartmentOf, c))
                    dept_objs: List[Department] = []
                    for d in dept_nodes:
                        if not isinstance(d, URIRef):
                            continue
                        dept = departments_index.get(d)
                        if dept is None:
                            d_id = ident(d)
                            d_name = self._label_or_fallback(g, d, default=d_id)
                            dept = Department(identifier=d_id, name=d_name)
                            # Courses (offerCourse); also try hasCourse if present in ABox
                            course_nodes = set(g.objects(d, BENCH.offerCourse)) | set(
                                g.objects(d, BENCH.hasCourse)
                            )
                            course_objs: List[Course] = []
                            for cr in course_nodes:
                                if not isinstance(cr, URIRef):
                                    continue
                                course = courses_index.get(cr)
                                if course is None:
                                    cr_id = ident(cr)
                                    title = self._label_or_warn(g, cr, default=cr_id)
                                    course = Course(identifier=cr_id, title=title)
                                    courses_index[cr] = course
                                course_objs.append(course)
                            object.__setattr__(dept, "courses", course_objs)
                            departments_index[d] = dept
                        dept_objs.append(dept)
                    object.__setattr__(college, "departments", dept_objs)
                    colleges_index[c] = college
                college_objs.append(college)

            object.__setattr__(uni, "colleges", college_objs)
            universities.append(uni)

        # Persons — include individuals typed as Person, Woman, or Man (no reasoning)
        person_nodes = (
            set(g.subjects(RDF.type, BENCH.Person))
            | set(g.subjects(RDF.type, BENCH.Woman))
            | set(g.subjects(RDF.type, BENCH.Man))
        )
        for p in person_nodes:
            if not isinstance(p, URIRef):
                continue
            person = persons_index.get(p)
            if person is None:
                first = self._required_dataprop(g, p, BENCH.hasFirstName, "hasFirstName")
                last = self._required_dataprop(g, p, BENCH.hasLastName, "hasLastName")
                email = self._required_dataprop(g, p, BENCH.hasEmailAddress, "hasEmailAddress")
                # Gender: Woman/Man classes
                is_woman: Optional[bool]
                if (p, RDF.type, BENCH.Woman) in g:
                    is_woman = True
                elif (p, RDF.type, BENCH.Man) in g:
                    is_woman = False
                else:
                    # Gender is required in our models; raise unless you prefer Optional[bool]
                    raise MappingError(
                        f"Missing gender class (Woman/Man) for person {p}. Cannot map required field 'is_woman'."
                    )
                hometown_lit = self._optional_dataprop(g, p, BENCH.isFrom)
                hometown = str(hometown_lit) if hometown_lit is not None else None

                person = Person(
                    identifier=ident(p),
                    first_name=first,
                    last_name=last,
                    email=email,
                    is_woman=bool(is_woman),
                    hometown=hometown,
                )
                persons_index[p] = person

        # Assemble world
        world = World()
        object.__setattr__(world, "universities", universities)
        object.__setattr__(world, "colleges", list(colleges_index.values()))
        object.__setattr__(world, "departments", list(departments_index.values()))
        object.__setattr__(world, "courses", list(courses_index.values()))
        object.__setattr__(world, "persons", list(persons_index.values()))
        return world

    # Helper methods
    @staticmethod
    def _label_or_fallback(g: Graph, node: URIRef, default: str) -> str:
        lbl = next(g.objects(node, RDFS.label), None)
        if isinstance(lbl, Literal):
            return str(lbl)
        return default

    @staticmethod
    def _label_or_warn(g: Graph, node: URIRef, default: str) -> str:
        lbl = next(g.objects(node, RDFS.label), None)
        if isinstance(lbl, Literal):
            return str(lbl)
        warnings.warn(
            f"Missing rdfs:label for {node}; falling back to identifier '{default}'.",
            stacklevel=2,
        )
        return default

    @staticmethod
    def _required_dataprop(g: Graph, s: URIRef, p: URIRef, name: str) -> str:
        lit = next(g.objects(s, p), None)
        if not isinstance(lit, Literal):
            raise MappingError(f"Missing required data property {name} for subject {s}.")
        return str(lit)

    @staticmethod
    def _optional_dataprop(g: Graph, s: URIRef, p: URIRef) -> Optional[Literal]:
        lit = next(g.objects(s, p), None)
        return lit if isinstance(lit, Literal) else None
