import itertools
import time
from typing import List

from krrood.entity_query_language.entity import (
    a,
    flatten,
    contains,
    set_of,
    the, let, entity, an, exists, and_
)
from krrood.entity_query_language.predicate import HasType
from krrood.entity_query_language.symbol_graph import SymbolGraph
from krrood.entity_query_language.symbolic import ResultQuantifier

from krrood_experiments.lubm.helpers import (
    evaluate_eql,
    load_instances_for_lubm_with_predicates,
)
from krrood_experiments.lubm.lubm_with_predicates import (
    GraduateStudent,
    Person,
    Publication,
    Professor,
    AssociateProfessor,
    Department,
    University,
    Student,
    Faculty,
    ResearchGroup,
    Chair,
    UndergraduateStudent,
)


def get_eql_queries() -> List[ResultQuantifier]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    q1 = an(entity(
        x := let(GraduateStudent, domain=None),
        flatten(x.takes_course).uri
        == "http://www.Department0.University0.edu/GraduateCourse0"
    ))

    # 2
    q2 = an(entity(
        x := let(GraduateStudent, domain=None),
        HasType(
            z := flatten(x.person.member_of), Department
        ),  # filtration of x producing z
        HasType(
            y := flatten(z.sub_organization_of), University
        ),  # filtration of z (which in turn filters x again) producing y
        contains(x.person.undergraduate_degree_from, y),  # join between x and y
    ))

    # 3
    q3 = an(entity(
        x := let(Publication, domain=None),
        flatten(x.publication_author).uri
        == "http://www.Department0.University0.edu/AssistantProfessor0",
    ))

    # 4
    q4 = a(
        set_of(
            (
                x := let(Professor, domain=None),
                name := x.name,
                email := x.person.email_address,
                telephone := x.person.telephone,
            ),
            flatten(x.works_for).uri == "http://www.Department0.University0.edu",
        )
    )

    # 5
    q5 = an(entity(
        x := let(Person, domain=None),
        flatten(x.member_of).uri == "http://www.Department0.University0.edu",
    ))

    # 6
    q6 = an(entity(x := let(Student, domain=None)))

    # 7
    associate_professor = the(entity(
        assoc_prof := let(AssociateProfessor, domain=None),
        assoc_prof.uri == "http://www.Department0.University0.edu/AssociateProfessor0"
    ))

    q7 = a(
        set_of(
            (
                x := let(Student, domain=None),
                y := flatten(x.takes_course),
            ),
            contains(associate_professor.teacher_of, y),
        )
    )

    # 8
    q8 = an(
        set_of(
            (
                x := let(Student, domain=None),
                y := flatten(x.person.member_of),
                z := x.person.email_address,
            ),
            HasType(y, Department),
            flatten(y.sub_organization_of).uri == "http://www.University0.edu",
        )
    )

    # 9
    q9 = a(
        set_of(
            (
                x := let(Student, domain=None),
                y := flatten(x.person.advisor),
                z := flatten(x.takes_course),
            ),
            HasType(y, Faculty),
            contains(
                y.teacher_of, z
            ),  # will benefit from symbol graph optimization
        )
    )

    # 10
    q10 = an(entity(
        x := let(Student, domain=None),
        flatten(x.takes_course).uri
        == "http://www.Department0.University0.edu/GraduateCourse0",
    ))

    # 11
    q11 = an(entity(
        x := let(ResearchGroup, domain=None),
        flatten(x.sub_organization_of).uri == "http://www.University0.edu",
    ))

    # 12
    q12 = an(
        set_of(
            (x := let(Chair, domain=None), y := flatten(x.works_for)),
            exists(y, and_(HasType(y, Department)
                   , flatten(y.sub_organization_of).uri == "http://www.University0.edu"))
            # flatten(y.sub_organization_of).uri == "http://www.University0.edu",
        )  # writing contains like this implies that the user knows that this is a set of objects.
        # A more declarative way would be to write SubOrganizationOf(y, the(University(name="University0"))).
    )

    # 13
    q13 = an(entity(
        x := flatten(the(entity(uni := let(University, domain=None), uni.uri == "http://www.University0.edu")).has_alumnus),
    ))

    # 14
    q14 = an(entity(x := let(UndergraduateStudent, domain=None)))

    eql_queries = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14]
    return eql_queries


def get_python_queries():
    """
    Legacy hand-written Python for q8. Kept for comparison.
    """
    students_data = (
        data for cls_, data in registry._by_class.items() if issubclass(cls_, Student)
    )
    flat_students_data = itertools.chain.from_iterable(students_data)
    q8 = (
        (student, m, student.person.email_address)
        for student in flat_students_data
        for m in student.person.member_of
        for u in m.sub_organization_of
        if isinstance(m, Department) and (u.uri == "http://www.University0.edu")
    )
    return [q8]


if __name__ == "__main__":
    registry = load_instances_for_lubm_with_predicates()
    python_start_time = time.time()
    count = None
    for pq in get_python_queries():
        count = len(list(pq))
    python_end_time = time.time()
    print(f"Python Count: {count}")
    print(f"Python Time elapsed: {python_end_time - python_start_time} seconds")
    start_time = time.time()
    counts, results, times = evaluate_eql(get_eql_queries())
    end_time = time.time()
    for i, n in enumerate(counts, 1):
        print(f"{i}:{n} ({times[i - 1]} sec)")
        # print([r for r in results[i - 1]])
    print(f"Time elapsed: {end_time - start_time} seconds")
