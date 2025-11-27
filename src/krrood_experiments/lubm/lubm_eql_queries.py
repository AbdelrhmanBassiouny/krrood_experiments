import itertools
import time
from dataclasses import dataclass
from typing import List

from krrood.entity_query_language.match import (
    match,
    select,
    select_any,
)
from krrood.entity_query_language.quantify_entity import (
    a,
    the,
)
from krrood.entity_query_language.symbolic import An, SetOf

from krrood_experiments.lubm.helpers import (
    evaluate_eql,
    load_instances_for_lubm_with_predicates,
    get_lubm_answers,
)
from krrood_experiments.lubm.lubm_with_predicates import (
    AssociateProfessor,
    Department,
    Student,
    GraduateStudent,
    University,
    Publication,
    Professor,
    Person,
    Faculty,
    Course,
    ResearchGroup,
    Chair,
    UndergraduateStudent,
)


@dataclass
class QueryWithSelectables:
    """
    This class is for being able to compare LUBM query answers with eql query answers.
    """

    query: An
    """
    The query to evaluate.
    """
    selectables: dict
    """
    A dictionary mapping variable names to selectables.
    """

    def evaluate(self):
        for value in self.query.evaluate():
            if isinstance(self.query._child_, SetOf):
                yield {k: value[v] for k, v in self.selectables.items()}
            else:
                yield {k: value for k, v in self.selectables.items()}


def get_eql_queries() -> List[QueryWithSelectables]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    # q1 = a(
    #     match(GraduateStudent)(
    #         takes_course=match()(
    #             uri="http://www.Department0.University0.edu/GraduateCourse0"
    #         )
    #     )
    # )
    # q1 = QueryWithSelectables(q1, {"X": q1})
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
    # q2 = QueryWithSelectables(q2, {"X": q2})
    #
    # # 3
    # q3 = a(
    #     match(Publication)(
    #         publication_author=match()(
    #             uri="http://www.Department0.University0.edu/AssistantProfessor0",
    #         )
    #     )
    # )
    # q3 = QueryWithSelectables(q3, {"X": q3})
    #
    # # 4
    # professor, name, email, telephone = select(Professor), select(), select(), select()
    # q4 = a(
    #     professor(
    #         works_for=match()(uri="http://www.Department0.University0.edu"),
    #         name=name,
    #         person=match()(
    #             email_address=email,
    #             telephone=telephone,
    #         ),
    #     )
    # )
    # q4 = QueryWithSelectables(
    #     q4, {"X": professor, "Y1": name, "Y2": email, "Y3": telephone}
    # )
    #
    # # 5
    # q5 = a(
    #     match(Person)(member_of=match()(uri="http://www.Department0.University0.edu"))
    # )
    # q5 = QueryWithSelectables(q5, {"X": q5})
    #
    # # 6
    # q6 = a(match(Student))

    # 7
    associate_professor = the(
        match(AssociateProfessor)(
            uri="http://www.Department0.University0.edu/AssociateProfessor0",
        )
    )
    student = select(Student)
    course = select(associate_professor.teacher_of)
    q7 = a(student(takes_course=course))

    q7 = QueryWithSelectables(q7, {"X": student, "Y": course})

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
    # q8 = QueryWithSelectables(q8, {"X": student, "Y1": department, "Y2": email})
    #
    # # 9
    # student, advisor, course = select(Student), select(Faculty), select(Course)
    # q9 = a(
    #     student(
    #         person=match()(advisor=advisor(teacher_of=course)),
    #         takes_course=course,
    #     )
    # )
    # q9 = QueryWithSelectables(q9, {"X": student, "Y1": advisor, "Y2": course})
    #
    # # 10
    # q10 = a(
    #     match(Student)(
    #         takes_course=match()(
    #             uri="http://www.Department0.University0.edu/GraduateCourse0",
    #         )
    #     )
    # )
    # q10 = QueryWithSelectables(q10, {"X": q10})
    #
    # # 11
    # q11 = a(
    #     match(ResearchGroup)(
    #         sub_organization_of=match()(uri="http://www.University0.edu")
    #     )
    # )
    # q11 = QueryWithSelectables(q11, {"X": q11})
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
    # q12 = QueryWithSelectables(q12, {"X": chair, "Y": department})
    #
    # # 13
    # has_alumnus = select()
    # q13 = a(
    #     match(University)(uri="http://www.University0.edu", has_alumnus=has_alumnus)
    # )
    # q13 = QueryWithSelectables(q13, {"X": has_alumnus})
    #
    # # 14
    # q14 = a(match(UndergraduateStudent))
    # q14 = QueryWithSelectables(q14, {"X": q14})

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


def report_python_query_time():
    python_start_time = time.time()
    count = None
    for pq in get_python_queries():
        count = len(list(pq))
    python_end_time = time.time()
    print(f"Python Count: {count}")
    print(f"Python Time elapsed: {python_end_time - python_start_time} seconds")


if __name__ == "__main__":
    registry = load_instances_for_lubm_with_predicates()
    # assert Chair in registry._by_class
    report_python_query_time()
    start_time = time.time()
    queries_with_selectables = get_eql_queries()
    counts, results, times = evaluate_eql(queries_with_selectables)
    end_time = time.time()
    for i, n in enumerate(counts, 1):
        print(f"{i}:{n} ({times[i - 1]} sec)")
        # print([r for r in results[i - 1]])
    print(f"Time elapsed: {end_time - start_time} seconds")

    lubm_answers = get_lubm_answers()
    uri_results = []
    for res in results[0]:
        uri_results.append({k: v.uri for k, v in res.items()})
    for sol in uri_results:
        assert sol in lubm_answers[7], f"{sol} not found in LUBM answers"
    for gt_sol in lubm_answers[7]:
        assert gt_sol in uri_results, f"{gt_sol} not found in EQL answers"
