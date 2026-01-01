def test_q22(world_from_graph_db):
    """
    Find all the students who took course taught by the Dean of the Organization.
    """
    results = set()
    for organization in world_from_graph_db.organizations:
        dean = organization.dean
        if dean:
            for course in world_from_graph_db.courses:
                if dean in course.teachers:
                    for person in world_from_graph_db.persons:
                        if course in person.takes_course:
                            results.add((person.identifier, course.identifier))

    assert len(results) == 106
