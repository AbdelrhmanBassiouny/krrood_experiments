import itertools
import time
from dataclasses import dataclass
from typing import List

import rdflib
from krrood.entity_query_language.entity import (
    entity,
    variable,
    set_of,
    contains,
    variable_from,
)
from krrood.entity_query_language.entity_result_processors import (
    a,
    an,
    the,
)
from krrood.entity_query_language.match import match_variable, match
from krrood.entity_query_language.symbolic import An, UnificationDict
from typing_extensions import Any

from krrood_experiments.lubm.helpers import (
    evaluate_eql,
    load_instances_for_lubm_with_predicates,
    get_lubm_answers,
)
from krrood_experiments.lubm.lubm_with_predicates import (
    Department,
    Student,
    GraduateStudent,
    University,
    Publication,
    Professor,
    Person,
    Course,
    Chair,
    Organization,
    AssociateProfessor,
    Faculty,
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
    takes_course = variable_from(grad_student.takes_course)
    q1 = an(
        entity(grad_student).where(
            takes_course.uri == "http://www.Department0.University0.edu/GraduateCourse0"
        )
    )
    q1 = QueryWithSelectables(q1, {"X": q1})

    # 2
    gs = variable(GraduateStudent, domain=None)
    member_of = variable(Department, domain=gs.person.member_of)
    under_graduate_degree_from = variable(
        University, domain=gs.person.undergraduate_degree_from
    )
    q2 = an(
        entity(gs).where(
            contains(member_of.sub_organization_of, under_graduate_degree_from)
        )
    )

    q2 = QueryWithSelectables(q2, {"X": q2})

    # 3
    publications = variable(Publication, domain=None)
    pub_author = variable_from(publications.publication_author)
    q3 = an(
        entity(publications).where(
            pub_author.uri
            == "http://www.Department0.University0.edu/AssistantProfessor0"
        )
    )
    q3 = QueryWithSelectables(q3, {"X": q3})

    # 4
    professor = variable(Professor, domain=None)
    works_for = variable_from(professor.works_for)
    q4 = a(
        set_of(
            professor,
            name := professor.name,
            email := professor.person.email_address,
            telephone := professor.person.telephone,
        ).where(works_for.uri == "http://www.Department0.University0.edu")
    )
    q4 = QueryWithSelectables(
        q4,
        {
            "X": professor,
            "Y1": name,
            "Y2": email,
            "Y3": telephone,
        },
    )

    # 5
    person = variable(Person, domain=None)
    member_of = variable_from(person.member_of)
    q5 = an(
        entity(person).where(member_of.uri == "http://www.Department0.University0.edu")
    )

    q5 = QueryWithSelectables(q5, {"X": q5})

    # 6
    q6 = an(entity(variable(Student, domain=None)))
    q6 = QueryWithSelectables(q6, {"X": q6})

    # 7
    AP = variable(AssociateProfessor, domain=None)
    associate_professor = the(
        entity(AP).where(
            AP.uri == "http://www.Department0.University0.edu/AssociateProfessor0"
        )
    )
    S = variable(Student, domain=None)
    TC = variable_from(S.takes_course)
    q7 = an(
        entity(S).where(
            contains(associate_professor.teacher_of, TC),
        )
    )
    q7 = QueryWithSelectables(q7, {"X": S, "Y": TC})

    # 8
    S = variable(Student, domain=None)
    member_of = variable(Department, domain=S.person.member_of)
    member_of_sub_organization_of = variable_from(member_of.sub_organization_of)
    q8 = a(
        set_of(S, member_of, email := S.person.email_address).where(
            member_of_sub_organization_of.uri == "http://www.University0.edu"
        )
    )
    q8 = QueryWithSelectables(q8, {"X": S, "Y1": member_of, "Y2": email})

    # 9
    S = variable(Student, domain=None)
    A = variable(Faculty, domain=S.person.advisor)
    TC = variable_from(S.takes_course)
    q9 = a(set_of(S, A, TC).where(contains(A.teacher_of, TC)))
    q9 = QueryWithSelectables(q9, {"X": S, "Y1": A, "Y2": TC})
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

    eql_queries = [q1, q2, q3, q4, q5, q6, q7, q8, q9]  # , q10, q11, q12, q13, q14]
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
