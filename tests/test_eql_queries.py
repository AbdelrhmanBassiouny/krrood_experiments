from owl2bench.model.organizations import Department
from owl2bench.model.college_disciplines import Engineering


def test_something(world_from_graph_db):

    departments = [
        x for x in world_from_graph_db.organizations if isinstance(x, Department)
    ]

    departments_with_engineering_courses = [
        x for x in departments if x.has_engineering_courses
    ]
