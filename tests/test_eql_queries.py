from owl2bench.model.organizations import Department
from owl2bench.model.college_disciplines import Engineering


def test_something(world_from_graph_db):

    engineering_courses = [
        c for c in world_from_graph_db.courses if isinstance(c.topic, Engineering)
    ]

    engineering_departments = [
        department
        for department in world_from_graph_db.organizations
        if isinstance(department, Department)
        and all([isinstance(c.topic, Engineering) for c in department.courses])
    ]

    print(sum(len(department.members) for department in engineering_departments))
    print(len({m.identifier for d in engineering_departments for m in d.members}))
    print(len(engineering_courses))
