import itertools
import time
from typing import List

from krrood.entity_query_language.entity import (
    a,
    flatten,
    contains,
    set_of,
    the,
    let,
    entity,
    an,
    exists,
    and_,
    match,
    SELECTED,
    select,
    select_any,
)
from krrood.entity_query_language.predicate import HasType
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
    Course,
    Organization,
)


def get_eql_queries() -> List[ResultQuantifier]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    q1 = a(
        match(GraduateStudent)(
            takes_course=match(Course)(
                uri="http://www.Department0.University0.edu/GraduateCourse0"
            )
        )
    )

    # 2
    q2 = a(
        match(GraduateStudent)(
            person=match(Person)(
                member_of=match(Department)(
                    sub_organization_of=(uni := match(University))
                ),
                undergraduate_degree_from=uni,
            )
        )
    )

    # 3
    q3 = a(
        match(Publication)(
            publication_author=match(Person)(
                uri="http://www.Department0.University0.edu/AssistantProfessor0",
            )
        )
    )

    # 4
    name, email, telephone = select(), select(), select()
    q4 = a(
        match(Professor)(
            works_for=match(Organization)(uri="http://www.Department0.University0.edu"),
            name=name,
            person=match(Person)(
                email_address=email,
                telephone=telephone,
            ),
        )
    )
    # q4 = a(
    #     set_of(
    #         (
    #             x := let(Professor, domain=None),
    #             name := x.name,
    #             email := x.person.email_address,
    #             telephone := x.person.telephone,
    #         ),
    #         flatten(x.works_for).uri == "http://www.Department0.University0.edu",
    #     )
    # )

    # 5
    q5 = a(
        match(Person)(
            member_of=match(Organization)(uri="http://www.Department0.University0.edu")
        )
    )

    # 6
    q6 = a(match(Student))

    # 7
    associate_professor = the(
        match(AssociateProfessor)(
            uri="http://www.Department0.University0.edu/AssociateProfessor0",
        )
    )

    q7 = a(
        match(Student)(
            takes_course=select_any(associate_professor.teacher_of),
        )
    )

    # q7 = a(
    #     set_of(
    #         (
    #             x := let(Student, domain=None),
    #             y := flatten(x.takes_course),
    #         ),
    #         contains(associate_professor.teacher_of, y),
    #     )
    # )

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
        match(Student)(
            person=match(Person)(
                advisor=select(Faculty)(teacher_of=(z := select(Course)))
            ),
            takes_course=z,
        )
    )

    # 10
    q10 = a(
        match(Student)(
            takes_course=match(Course)(
                uri="http://www.Department0.University0.edu/GraduateCourse0",
            )
        )
    )

    # 11
    q11 = a(
        match(ResearchGroup)(
            sub_organization_of=match(Organization)(uri="http://www.University0.edu")
        )
    )

    # 12
    q12 = a(
        match(Chair)(
            works_for=select(Department)(
                sub_organization_of=match(Organization)(
                    uri="http://www.University0.edu"
                )
            )
        )
    )

    # 13
    uni = the(match(University)(uri="http://www.University0.edu"))
    q13 = an(entity(uni.has_alumnus))

    # 14
    q14 = a(match(UndergraduateStudent))

    eql_queries = [q1, q2, q3, q4, q5, q6, q6, q8, q9, q10, q11, q12, q13, q14]
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
    # assert Chair in registry._by_class
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
