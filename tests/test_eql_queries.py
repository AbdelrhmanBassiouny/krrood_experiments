from krrood.entity_query_language.entity import entity, variable, contains
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.predicate import HasType
from krrood.entity_query_language.symbolic import Variable

from model.base import Course
from model.college_disciplines import Engineering
from model.programs import UndergraduateProgram
from owl2bench.model.base import Person


def test_something(world_from_graph_db):
    p = variable(Person, world_from_graph_db.persons)
    courses = variable(Course, world_from_graph_db.courses)
    engineering_course = an(entity(courses).where(HasType(courses.topic, Engineering)))
    r = an(entity(p).where(contains(p.takes_course, engineering_course)))
    print(len(list(r.evaluate())))

    print(
        [
            p
            for p in world_from_graph_db.persons
            if any(
                course
                for course in p.takes_course
                if isinstance(course.topic, Engineering)
            )
        ]
    )
    print([c.topic for c in world_from_graph_db.courses])
