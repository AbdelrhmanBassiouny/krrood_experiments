from krrood.entity_query_language.entity import entity, variable, contains
from krrood.entity_query_language.entity_result_processors import an
from krrood.entity_query_language.symbolic import Variable

from model.programs import UndergraduateProgram
from owl2bench.model.base import Person


def test_something(world_from_graph_db):
    p = variable(Person, world_from_graph_db.persons)
    ug_program = variable(UndergraduateProgram, world_from_graph_db.programs)
    r = an(entity(p).where(contains(p.enrolled_in, ug_program)))
    print(len(list(r.evaluate())))
    print(
        [p for p in world_from_graph_db.programs if isinstance(p, UndergraduateProgram)]
    )
