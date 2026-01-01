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
from krrood.entity_query_language.predicate import HasType
from krrood.entity_query_language.symbolic import An, UnificationDict
from typing_extensions import Any, Optional

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
    Chair,
    AssociateProfessor,
    Faculty,
    ResearchGroup,
    UndergraduateStudent,
    AssistantProfessor,
    FullProfessor, Organization, Employee,
)
from krrood_experiments.lubm.owl_instances_loader import OwlInstancesRegistry


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


def get_eql_queries(
    registry_: Optional[OwlInstancesRegistry] = None,
) -> List[QueryWithSelectables]:
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
    grad_student = variable(GraduateStudent, domain=None)
    member_of = variable_from(grad_student.member_of)
    under_graduate_degree_from = variable_from(grad_student.undergraduate_degree_from)
    q2 = an(
        entity(grad_student).where(
            HasType(member_of, Department),
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
    professor = variable(
        Professor,
        domain=None,
    )
    works_for = variable_from(professor.works_for)
    q4 = a(
        set_of(
            professor,
            name := professor.name,
            email := professor.email_address,
            telephone := professor.telephone,
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

    q5 = QueryWithSelectables(q5, {"X": person})

    # 6
    student = variable(Student, domain=None)
    q6 = an(entity(student))
    q6 = QueryWithSelectables(q6, {"X": student})

    # 7
    associate_professor = variable(AssociateProfessor, domain=None)
    the_associate_professor = the(
        entity(associate_professor).where(
            associate_professor.uri
            == "http://www.Department0.University0.edu/AssociateProfessor0"
        )
    )
    student = variable(Student, domain=None)
    student_course = variable_from(student.takes_course)
    q7 = a(
        set_of(student, student_course).where(
            contains(the_associate_professor.teacher_of, student_course),
        )
    )
    q7 = QueryWithSelectables(q7, {"X": student, "Y": student_course})

    # 8
    student = variable(Student, domain=None)
    member_of = variable_from(student.member_of)
    member_of_sub_organization_of = variable_from(member_of.sub_organization_of)
    q8 = a(
        set_of(student, member_of, email := student.email_address).where(
            HasType(member_of, Department),
            member_of_sub_organization_of.uri == "http://www.University0.edu"
        )
    )
    q8 = QueryWithSelectables(q8, {"X": student, "Y": member_of, "Z": email})

    # 9
    student = variable(Student, domain=None)
    advisor = variable_from(student.advisor)
    takes_course = variable_from(student.takes_course)
    q9 = a(
        set_of(student, advisor, takes_course).where(
            contains(advisor.teacher_of, takes_course)
        )
    )
    q9 = QueryWithSelectables(q9, {"X": student, "Y": advisor, "Z": takes_course})

    # 10
    student = variable(Student, domain=None)
    takes_course = variable_from(student.takes_course)
    q10 = an(
        entity(student).where(
            takes_course.uri == "http://www.Department0.University0.edu/GraduateCourse0"
        )
    )
    q10 = QueryWithSelectables(q10, {"X": student})

    # 11
    research_group = variable(ResearchGroup, domain=None)
    sub_organization_of = variable_from(research_group.sub_organization_of)
    q11 = an(
        entity(research_group).where(
            sub_organization_of.uri == "http://www.University0.edu"
        )
    )
    q11 = QueryWithSelectables(q11, {"X": research_group})

    # 12
    chair = variable(Chair, domain=None)
    works_for = variable_from(chair.works_for)
    sub_organization_of = variable_from(works_for.sub_organization_of)
    q12 = a(
        set_of(chair, works_for).where(
            HasType(works_for, Department),
            sub_organization_of.uri == "http://www.University0.edu"
        )
    )
    q12 = QueryWithSelectables(q12, {"X": chair, "Y": works_for})

    # 13
    university = variable(University, domain=None)
    the_university = the(
        entity(university).where(university.uri == "http://www.University0.edu")
    )
    university_alumni = variable_from(the_university.has_alumnus)
    q13 = an(entity(university_alumni))
    q13 = QueryWithSelectables(q13, {"X": university_alumni})

    # 14
    undergraduate_student = variable(UndergraduateStudent, domain=None)
    q14 = an(entity(undergraduate_student))
    q14 = QueryWithSelectables(q14, {"X": undergraduate_student})

    eql_queries = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14]
    return eql_queries
    # return [q4]


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
    queries_with_selectables = get_eql_queries(registry)
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
            assert sol in lubm_answers[i], f"{sol} not found in LUBM answers, for query {i}"
        for gt_sol in lubm_answers[i]:
            assert (
                gt_sol in uri_results
            ), f"{gt_sol} not found in EQL answers, for query {i}"
        assert len(lubm_answers[i]) == len(uri_results), f"Number of results mismatch for query {i}"
