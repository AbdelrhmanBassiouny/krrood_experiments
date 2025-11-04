import re
from owl2bench import InstanceGenerator, InstanceConfig, Range


def test_determinism_fixed_seed():
    config = InstanceConfig(
        colleges=Range(2, 2),
        departments=Range(2, 2),
        undergraduate_students=Range(2, 2),
        postgraduate_students=Range(1, 1),
        phd_students=Range(1, 1),
        courses=Range(2, 2),
        women_college_ratio=0.5,
    )
    gen1 = InstanceGenerator(config=config, seed=42)
    gen2 = InstanceGenerator(config=config, seed=42)

    u1 = gen1.generate(universities=1)
    u2 = gen2.generate(universities=1)

    # Exact structural equality by mapping to simple dicts
    def snapshot(unis):
        data = []
        for u in unis:
            data.append((
                u.identifier,
                u.name,
                [
                    (
                        c.identifier,
                        c.name,
                        c.is_women_only,
                        [
                            (
                                d.identifier,
                                d.name,
                                tuple((crs.identifier, crs.title) for crs in d.courses),
                                tuple((p.identifier, p.first_name, p.last_name, p.email, p.is_woman) for p in d.undergraduate_students),
                                tuple((p.identifier, p.first_name, p.last_name, p.email, p.is_woman) for p in d.postgraduate_students),
                                tuple((p.identifier, p.first_name, p.last_name, p.email, p.is_woman) for p in d.phd_students),
                            )
                            for d in c.departments
                        ],
                    )
                    for c in u.colleges
                ],
            ))
        return tuple(data)

    assert snapshot(u1) == snapshot(u2)


def test_counts_within_ranges():
    config = InstanceConfig(
        colleges=Range(2, 3),
        departments=Range(1, 2),
        undergraduate_students=Range(1, 3),
        postgraduate_students=Range(0, 1),
        phd_students=Range(0, 1),
        courses=Range(1, 2),
        women_college_ratio=0.0,
    )
    gen = InstanceGenerator(config=config, seed=7)
    universities = gen.generate(universities=3)

    assert len(universities) == 3
    for u in universities:
        assert config.colleges.minimum <= len(u.colleges) <= config.colleges.maximum
        for c in u.colleges:
            assert config.departments.minimum <= len(c.departments) <= config.departments.maximum
            for d in c.departments:
                assert config.courses.minimum <= len(d.courses) <= config.courses.maximum
                assert config.undergraduate_students.minimum <= len(d.undergraduate_students) <= config.undergraduate_students.maximum
                assert config.postgraduate_students.minimum <= len(d.postgraduate_students) <= config.postgraduate_students.maximum
                assert config.phd_students.minimum <= len(d.phd_students) <= config.phd_students.maximum


def test_women_only_college_enforces_gender():
    config = InstanceConfig(
        colleges=Range(1, 1),
        departments=Range(1, 1),
        undergraduate_students=Range(5, 5),
        postgraduate_students=Range(2, 2),
        phd_students=Range(1, 1),
        courses=Range(1, 1),
        women_college_ratio=1.0,  # always women-only
    )
    gen = InstanceGenerator(config=config, seed=123)
    universities = gen.generate(universities=1)
    college = universities[0].colleges[0]
    assert college.is_women_only is True
    dept = college.departments[0]

    for group in (dept.undergraduate_students, dept.postgraduate_students, dept.phd_students):
        assert len(group) > 0
        assert all(p.is_woman for p in group)


def test_email_and_full_name_format():
    config = InstanceConfig(
        colleges=Range(1, 1),
        departments=Range(1, 1),
        undergraduate_students=Range(1, 1),
        postgraduate_students=Range(0, 0),
        phd_students=Range(0, 0),
        courses=Range(1, 1),
        women_college_ratio=0.0,
    )
    gen = InstanceGenerator(config=config, seed=1)
    universities = gen.generate(universities=1)
    person = universities[0].colleges[0].departments[0].undergraduate_students[0]

    assert person.full_name == f"{person.first_name} {person.last_name}"
    assert re.match(r"^[a-z0-9_]+@bench\.com$", person.email)
