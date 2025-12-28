def test_q14(world_from_graph_db):

    leisure_students = filter(
        lambda p: len(p.takes_course) == 1,
        world_from_graph_db.persons,
    )
    print(len(list(leisure_students)))
