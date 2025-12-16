import itertools
import time
from dataclasses import dataclass
from typing import List

import rdflib
from krrood.entity_query_language.entity import entity, variable, exists, flatten, and_, set_of, contains
from krrood.entity_query_language.entity_result_processors import (
    a,
    the, an,
)
from krrood.entity_query_language.match import (
    match_variable, match,
)
from krrood.entity_query_language.predicate import HasType
from krrood.entity_query_language.symbolic import An, UnificationDict
from typing_extensions import Any

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
    UndergraduateStudent, Organization,
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
            if isinstance(value, UnificationDict):
                yield {k: value[v] for k, v in self.selectables.items()}
            else:
                yield {k: value for k, v in self.selectables.items()}


def get_eql_queries() -> List[QueryWithSelectables]:
    # 1 (No joining, just filtration of graduate students through taking a certain course)
    grad_student = variable(GraduateStudent, domain=None)
    takes_course = variable(Course, domain=grad_student.takes_course)
    q1 = an(entity(grad_student).where(takes_course.uri == "http://www.Department0.University0.edu/GraduateCourse0"))
    q1 = QueryWithSelectables(q1, {"X": q1})

    # 2
    gs = variable(GraduateStudent, domain=None)
    member_of = variable(Department, domain=gs.person.member_of)
    under_graduate_degree_from = variable(University, domain=gs.person.undergraduate_degree_from)
    q2 = an(entity(gs).where(contains(member_of.sub_organization_of, under_graduate_degree_from)))

    q2 = QueryWithSelectables(q2, {"X": q2})

    #3
    publications = variable(Publication, domain=None)
    pub_author = variable(Person, domain=publications.publication_author)
    q3 = an(entity(publications).where(pub_author.uri == "http://www.Department0.University0.edu/AssistantProfessor0"))
    q3 = QueryWithSelectables(q3, {"X": q3})

    # 4
    professor = variable(Professor, domain=None)
    works_for = variable(Organization, domain=professor.works_for)
    q4 = a(set_of(professor,
                  name := professor.name,
                  email := professor.person.email_address,
                  telephone := professor.person.telephone).where(works_for.uri == "http://www.Department0.University0.edu"))
    q4 = QueryWithSelectables(
        q4,
        {
            "X": professor,
            "Y1": name,
            "Y2": email,
            "Y3": telephone,
        },
    )

    # # 5
    # q5 = a(
    #     matching(Person)(
    #         member_of=matching()(uri="http://www.Department0.University0.edu")
    #     )
    # )
    # q5 = QueryWithSelectables(q5, {"X": q5})
    #
    # # 6
    # q6 = a(matching(Student))
    # q6 = QueryWithSelectables(q6, {"X": q6})
    #
    # # 7
    # associate_professor = the(
    #     matching(AssociateProfessor)(
    #         uri="http://www.Department0.University0.edu/AssociateProfessor0",
    #     )
    # )
    # q7 = a(
    #     matching(Student)(
    #         takes_course=associate_professor.teacher_of,
    #     )
    # )
    # q7 = QueryWithSelectables(q7, {"X": q7, "Y": q7.takes_course})
    #
    # # 8
    # q8 = a(
    #     matching(Student)(
    #         person=matching()(
    #             member_of=matching(Department)(
    #                 sub_organization_of=matching()(uri="http://www.University0.edu")
    #             ),
    #         )
    #     )
    # )
    # q8 = QueryWithSelectables(
    #     q8, {"X": q8, "Y1": q8.person.member_of, "Y2": q8.person.email_address}
    # )
    #
    # # 9
    # course = matching(Course)
    # q9 = a(
    #     matching(Student)(
    #         person=matching()(advisor=matching(Faculty)(teacher_of=course)),
    #         takes_course=course,
    #     )
    # )
    # q9 = QueryWithSelectables(
    #     q9, {"X": q9, "Y1": q9.person.advisor, "Y2": q9.takes_course}
    # )
    #
    # # 10
    # q10 = a(
    #     matching(Student)(
    #         takes_course=matching()(
    #             uri="http://www.Department0.University0.edu/GraduateCourse0",
    #         )
    #     )
    # )
    # q10 = QueryWithSelectables(q10, {"X": q10})
    #
    # # 11
    # q11 = a(
    #     matching(ResearchGroup)(
    #         sub_organization_of=matching()(uri="http://www.University0.edu")
    #     )
    # )
    # q11 = QueryWithSelectables(q11, {"X": q11})
    #
    # # 12
    # q12 = a(
    #     matching(Chair)(
    #         works_for=matching(Department)(
    #             sub_organization_of=matching()(uri="http://www.University0.edu")
    #         )
    #     )
    # )
    # q12 = QueryWithSelectables(q12, {"X": q12, "Y": q12.works_for})
    #
    # # 13
    # q13 = a(matching(University)(uri="http://www.University0.edu"))
    # q13 = QueryWithSelectables(q13, {"X": q13})
    #
    # # 14
    # q14 = a(matching(UndergraduateStudent))
    # q14 = QueryWithSelectables(q14, {"X": q14})

    eql_queries = [q1, q2, q3, q4] #q5, q6, q7, q8, q9, q10, q11, q12, q13, q14]
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


def report_python_query_time():
    python_start_time = time.time()
    count = None
    for pq in get_python_queries():
        count = len(list(pq))
    python_end_time = time.time()
    print(f"Python Count: {count}")
    print(f"Python Time elapsed: {python_end_time - python_start_time} seconds")


def process_value_for_lubm_answer_comparison(value: Any):
    if hasattr(value, "uri"):
        return value.uri
    elif isinstance(value, rdflib.Literal):
        return value.value
    else:
        return value


if __name__ == "__main__":
    registry = load_instances_for_lubm_with_predicates()
    assert Chair in registry._by_class
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
    for i, query_results in enumerate(results, 1):
        uri_results = []
        for res in query_results:
            uri_results.append(
                {k: process_value_for_lubm_answer_comparison(v) for k, v in res.items()}
            )
        for sol in uri_results:
            assert (
                sol in lubm_answers[i]
            ), f"{sol} not found in LUBM answers, for query {i}"
        for gt_sol in lubm_answers[i]:
            assert (
                gt_sol in uri_results
            ), f"{gt_sol} not found in EQL answers, for query {i}"
