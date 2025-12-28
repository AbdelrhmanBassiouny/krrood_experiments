from owl2bench.model.college_disciplines import Engineering


def test_something(world_from_graph_db):
    print(
        len(
            [
                p
                for p in world_from_graph_db.persons
                if any(
                    isinstance(course.topic, Engineering) for course in p.takes_course
                )
            ]
        )
    )
