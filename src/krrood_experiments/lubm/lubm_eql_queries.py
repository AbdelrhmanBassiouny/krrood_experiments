import itertools
import time
from typing import List

from krrood.entity_query_language.quantify_entity import (
    a,
    the,
)
from krrood.entity_query_language.match import (
    match,
    select,
    select_any,
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
    # q1 = a(
    #     match(GraduateStudent)(
    #         takes_course=match()(
    #             uri="http://www.Department0.University0.edu/GraduateCourse0"
    #         )
    #     )
    # )
    #
    # # 2
    # uni = match(University)
    # q2 = a(
    #     match(GraduateStudent)(
    #         person=match()(
    #             member_of=match(Department)(sub_organization_of=uni),
    #             undergraduate_degree_from=uni,
    #         )
    #     )
    # )
    #
    # # 3
    # q3 = a(
    #     match(Publication)(
    #         publication_author=match()(
    #             uri="http://www.Department0.University0.edu/AssistantProfessor0",
    #         )
    #     )
    # )
    #
    # # 4
    # name, email, telephone = select(), select(), select()
    # q4 = a(
    #     match(Professor)(
    #         works_for=match()(uri="http://www.Department0.University0.edu"),
    #         name=name,
    #         person=match()(
    #             email_address=email,
    #             telephone=telephone,
    #         ),
    #     )
    # )
    #
    # # 5
    # q5 = a(
    #     match(Person)(member_of=match()(uri="http://www.Department0.University0.edu"))
    # )
    #
    # # 6
    # q6 = a(match(Student))

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

    # 8
    # student, department, email = select(Student), select(Department), select()
    # q8 = a(
    #     student(
    #         person=match()(
    #             member_of=department(
    #                 sub_organization_of=match()(uri="http://www.University0.edu")
    #             ),
    #             email_address=email,
    #         )
    #     )
    # )
    #
    # # 9
    # student, advisor, course = select(Student), select(Faculty), select(Course)
    # q9 = a(
    #     student(
    #         person=match()(advisor=advisor(teacher_of=course)),
    #         takes_course=course,
    #     )
    # )
    #
    # # 10
    # q10 = a(
    #     match(Student)(
    #         takes_course=match()(
    #             uri="http://www.Department0.University0.edu/GraduateCourse0",
    #         )
    #     )
    # )
    #
    # # 11
    # q11 = a(
    #     match(ResearchGroup)(
    #         sub_organization_of=match()(uri="http://www.University0.edu")
    #     )
    # )
    #
    # # 12
    # chair, department = select(Chair), select(Department)
    # q12 = a(
    #     chair(
    #         works_for=department(
    #             sub_organization_of=match()(uri="http://www.University0.edu")
    #         )
    #     )
    # )
    #
    # # 13
    # has_alumnus = select()
    # q13 = a(
    #     match(University)(uri="http://www.University0.edu", has_alumnus=has_alumnus)
    # )
    #
    # # 14
    # q14 = a(match(UndergraduateStudent))

    # eql_queries = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14]
    # return eql_queries
    return [q7]


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
