import itertools
import time
from typing import List

from krrood.entity_query_language.quantify_entity import (
    a,
    the,
)
from krrood.entity_query_language.match import (
    select,
    matching,
    match_any,
)

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
        matching(GraduateStudent)(
            takes_course=matching()(
                uri="http://www.Department0.University0.edu/GraduateCourse0"
            )
        )
    )

    # 2
    uni = matching(University)
    q2 = a(
        matching(GraduateStudent)(
            person=matching()(
                member_of=matching(Department)(sub_organization_of=uni),
                undergraduate_degree_from=uni,
            )
        )
    )

    # 3
    q3 = a(
        matching(Publication)(
            publication_author=matching()(
                uri="http://www.Department0.University0.edu/AssistantProfessor0",
            )
        )
    )

    # 4
    q4 = a(
        matching(Professor)(
            works_for=matching()(uri="http://www.Department0.University0.edu"),
        )
    )
    q4 = select(q4, q4.name, q4.person.email_address, q4.person.telephone)

    # 5
    q5 = a(
        matching(Person)(
            member_of=matching()(uri="http://www.Department0.University0.edu")
        )
    )

    # 6
    q6 = a(matching(Student))

    # 7
    associate_professor = the(
        matching(AssociateProfessor)(
            uri="http://www.Department0.University0.edu/AssociateProfessor0",
        )
    )
    q7 = a(
        matching(Student)(
            takes_course=associate_professor.teacher_of,
        )
    )
    q7 = select(q7, q7.takes_course)

    # 8
    q8 = a(
        matching(Student)(
            person=matching()(
                member_of=matching(Department)(
                    sub_organization_of=matching()(uri="http://www.University0.edu")
                ),
            )
        )
    )
    q8 = select(q8, q8.person.member_of, q8.person.email_address)

    # 9
    course = matching(Course)
    q9 = a(
        matching(Student)(
            person=matching()(advisor=matching(Faculty)(teacher_of=course)),
            takes_course=course,
        )
    )
    q9 = select(q9, q9.person.advisor, q9.takes_course)

    # 10
    q10 = a(
        matching(Student)(
            takes_course=matching()(
                uri="http://www.Department0.University0.edu/GraduateCourse0",
            )
        )
    )

    # 11
    q11 = a(
        matching(ResearchGroup)(
            sub_organization_of=matching()(uri="http://www.University0.edu")
        )
    )

    # 12
    q12 = a(
        matching(Chair)(
            works_for=matching(Department)(
                sub_organization_of=matching()(uri="http://www.University0.edu")
            )
        )
    )
    q12 = select(q12, q12.works_for)

    # 13
    q13 = a(matching(University)(uri="http://www.University0.edu"))
    select(q13.has_alumnus)

    # 14
    q14 = a(matching(UndergraduateStudent))

    eql_queries = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14]
    return eql_queries
    # return [q7]


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
