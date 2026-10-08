"""
Tests of the agent-loop experiment: the scenario generator, the path planner, the code-size measurement, and the
agreement of the decisions of the variants on a few steps.

The KRROOD test loads the OWL2Bench data in its own process (about 15 s). The GraphDB tests need a GraphDB server
(``KRROOD_GRAPHDB_URL``) and load the raw data into it, which takes about 20 minutes with the owl2-rl-optimized ruleset;
they run only when ``AGENT_LOOP_GRAPHDB_TESTS=1``. The reasonable test needs ``reasonable`` and about 5 minutes; it runs
only when ``AGENT_LOOP_REASONABLE_TESTS=1``. The Nemo test needs Nemo's ``nmo`` (``NEMO_BINARY``) and about a minute.

Run with::

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/aamas27/test_agent_loop.py
"""

from __future__ import annotations

import json
import math
import os
import random
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import requests

from krrood_experiments.aamas27.agent_loop.campus import CampusMap, PathPlanner, Place, PlaceKind
from krrood_experiments.aamas27.agent_loop.events import CourseTaking, CricketEnthusiasm, Enrollment
from krrood_experiments.aamas27.agent_loop.measurement import code_lines, distribution, sparql_tokens
from krrood_experiments.aamas27.agent_loop.nemo_variant import step_program
from krrood_experiments.aamas27.agent_loop.robot import (
    Action,
    ActionKind,
    DeliveryPolicy,
    HandoutCandidate,
    Robot,
    TicketCandidate,
)
from krrood_experiments.aamas27.agent_loop.scenario import (
    NEW_PERSON_PREFIX,
    Scenario,
    generate_scenario,
    read_university_data,
)
from krrood_experiments.aamas27.environment import EXPERIMENTS_ROOT, UNREASONED_FILE
from krrood_experiments.aamas27.graphdb import DEFAULT_GRAPHDB_URL
from krrood_experiments.aamas27.loading_worker import NEMO_RULES

DRIVER = EXPERIMENTS_ROOT / "scripts" / "aamas27" / "run_agent_loop.py"


@pytest.fixture(scope="module")
def university():
    return read_university_data(UNREASONED_FILE)


@pytest.fixture(scope="module")
def scenario(university):
    return generate_scenario(UNREASONED_FILE, steps=60, seed=7, university=university)


def test_same_seed_gives_the_same_scenario(university):
    first = generate_scenario(UNREASONED_FILE, steps=30, seed=3, university=university)
    second = generate_scenario(UNREASONED_FILE, steps=30, seed=3, university=university)
    assert json.dumps(first.to_json()) == json.dumps(second.to_json())


def test_another_seed_gives_other_events(university):
    first = generate_scenario(UNREASONED_FILE, steps=30, seed=3, university=university)
    second = generate_scenario(UNREASONED_FILE, steps=30, seed=4, university=university)
    assert [p.to_json() for p in first.perceptions] != [p.to_json() for p in second.perceptions]


def test_scenario_survives_a_json_round_trip(scenario, tmp_path):
    path = tmp_path / "scenario.json"
    scenario.write(path)
    assert json.dumps(Scenario.read(path).to_json()) == json.dumps(scenario.to_json())


def test_university_data_has_the_owl2bench_structure(university):
    assert len(university.departments_by_college) == 6
    assert sum(len(d) for d in university.departments_by_college.values()) == 21
    assert sum(len(c) for c in university.courses_by_department.values()) == 858
    assert len(university.students) == 989
    assert len(university.cricket_enthusiasts) == 20


def test_every_place_is_connected_to_a_dock(scenario):
    distances = PathPlanner(scenario.campus).dijkstra(scenario.campus.docks)
    assert set(distances) == set(scenario.campus.places)


def test_every_course_is_taught_in_a_classroom_of_its_department(scenario, university):
    for department, courses in university.courses_by_department.items():
        classrooms = set(scenario.campus.department_classrooms[department])
        for course in courses:
            assert scenario.course_rooms[course] in classrooms
            assert scenario.campus.place(scenario.course_rooms[course]).kind is PlaceKind.CLASSROOM


def test_every_person_has_a_mailbox_room(scenario, university):
    for person in university.department_of_person:
        assert scenario.campus.place(scenario.mailbox_of(person)).is_room


def test_every_event_adds_a_new_fact(scenario, university):
    courses_taken = set(university.courses_taken)
    enthusiasts = set(university.cricket_enthusiasts)
    new_people = set()
    for perception in scenario.perceptions:
        assert len(perception.knowledge_events) == scenario.events_per_step
        assert perception.requested_college in university.departments_by_college
        for event in perception.knowledge_events:
            if isinstance(event, Enrollment):
                assert event.person.startswith(NEW_PERSON_PREFIX) and event.person not in new_people
                assert event.person not in university.department_of_person
                new_people.add(event.person)
                assert scenario.mailbox_of(event.person) == scenario.campus.department_offices[event.department]
            elif isinstance(event, CourseTaking):
                assert (event.student, event.course) not in courses_taken
                assert event.student in university.students or event.student in new_people
                courses_taken.add((event.student, event.course))
            elif isinstance(event, CricketEnthusiasm):
                assert event.person not in enthusiasts and event.person not in university.cricket_haters
                enthusiasts.add(event.person)
    kinds = {event.kind for perception in scenario.perceptions for event in perception.knowledge_events}
    assert len(kinds) == 3


def small_campus() -> CampusMap:
    campus = CampusMap()
    places = [campus.add_place(Place(f"p{i}", PlaceKind.CORRIDOR, "b", float(i), 0.0)) for i in range(6)]
    random_generator = random.Random(1)
    for first in range(6):
        for second in range(first + 1, 6):
            if random_generator.random() < 0.6:
                campus.connect(places[first], places[second], random_generator.uniform(1, 10))
    campus.docks.append("p0")
    return campus


def test_planner_finds_shortest_paths():
    campus = small_campus()
    names = list(campus.places)
    shortest = {(a, b): (0.0 if a == b else campus.neighbours[a].get(b, math.inf)) for a in names for b in names}
    for middle in names:
        for a in names:
            for b in names:
                shortest[a, b] = min(shortest[a, b], shortest[a, middle] + shortest[middle, b])
    planner = PathPlanner(campus)
    for a in names:
        for b in names:
            assert planner.distance(campus.place(a), campus.place(b)) == pytest.approx(shortest[a, b])


def test_policy_prefers_the_nearest_undelivered_item(scenario):
    robot = Robot.at_start(scenario.robot, scenario.campus)
    policy = DeliveryPolicy()
    handouts = [HandoutCandidate("s", "c1", "U0C0D0-classroom-0", 30.0)]
    tickets = [TicketCandidate("p", "U0C0D0-office", 20.0)]
    action = policy.decide(robot, "college", handouts, tickets)
    assert action == Action(ActionKind.DELIVER_TICKET, "U0C0D0-office", ("p",))
    policy.act(robot, action)
    assert policy.decide(robot, "college", handouts, tickets).kind is ActionKind.DELIVER_HANDOUTS
    robot.battery_metres = 1.0
    assert policy.decide(robot, "college", handouts, tickets).kind is ActionKind.CHARGE


def test_code_lines_ignore_docstrings_comments_and_decorators():
    source = textwrap.dedent(
        '''
        @decorator
        def function(x):
            """
            Docstring.
            """
            # a comment
            y = x + 1

            return y
        '''
    )
    assert code_lines(source) == 3


def test_sparql_tokens_ignore_prefixes():
    query = "PREFIX a: <http://a#>\nSELECT ?x WHERE { ?x a:p <http://b> . }"
    assert sparql_tokens(query) == ["SELECT", "?x", "WHERE", "{", "?x", "a:p", "<http://b>", ".", "}"]


def test_distribution_percentiles():
    values = list(range(1, 101))
    summary = distribution(values)
    assert summary["median"] == 50.5 and summary["p95"] == 95 and summary["total"] == 5050


KRROOD_AGAINST_PLAIN_PYTHON = textwrap.dedent(
    """
    import json, os, sys
    os.environ["TQDM_DISABLE"] = "1"
    from pathlib import Path
    from krrood.entity_query_language.symbol_graph import SymbolGraph
    from krrood_experiments.aamas27.agent_loop.krrood_variant import KrroodVariant
    from krrood_experiments.aamas27.agent_loop.loop import run_agent_loop
    from krrood_experiments.aamas27.agent_loop.robot import Robot, can_reach, travel_seconds
    from krrood_experiments.aamas27.agent_loop.scenario import Scenario
    from krrood_experiments.owl2bench.ontomatic import owl2bench_with_predicates as model

    scenario = Scenario.read(Path(sys.argv[1]))
    robot = Robot.at_start(scenario.robot, scenario.campus)
    variant = KrroodVariant(scenario=scenario, robot=robot)
    mismatches = []

    original_handouts = variant.handout_candidates
    def handouts_with_check(college_iri, meter):
        found = original_handouts(college_iri, meter)
        college = variant._resolve(college_iri, model.Organization)
        expected = {
            (student.uri, course.uri, course.taught_in.identifier, travel_seconds(robot, course.taught_in))
            for student in SymbolGraph().get_instances_of_type(model.Student)
            if college in student.is_member_of
            for course in student.takes_course
            if can_reach(robot, course.taught_in)
        }
        actual = {(c.student, c.course, c.room, c.travel_seconds) for c in found}
        if expected != actual:
            mismatches.append(("handouts", len(expected), len(actual)))
        return found

    original_tickets = variant.ticket_candidates
    def tickets_with_check(meter):
        found = original_tickets(meter)
        expected = {
            (person.uri, person.mailbox.identifier, travel_seconds(robot, person.mailbox))
            for person in SymbolGraph().get_instances_of_type(model.Person)
            if any(str(interest.uri).endswith("#T20Cricket") for interest in person.is_crazy_about)
            and can_reach(robot, person.mailbox)
        }
        actual = {(c.person, c.room, c.travel_seconds) for c in found}
        if expected != actual:
            mismatches.append(("tickets", len(expected), len(actual)))
        return found

    variant.handout_candidates = handouts_with_check
    variant.ticket_candidates = tickets_with_check
    result = run_agent_loop(variant)
    print(json.dumps({"mismatches": mismatches, "steps": len(result.steps),
                      "handouts": [s["handout_candidates"] for s in result.steps],
                      "tickets": [s["ticket_candidates"] for s in result.steps]}))
    sys.stdout.flush()
    os._exit(0)
    """
)


def test_krrood_queries_equal_plain_python_over_the_same_objects(university, tmp_path):
    scenario = generate_scenario(UNREASONED_FILE, steps=6, seed=11, university=university)
    scenario_file = tmp_path / "scenario.json"
    scenario.write(scenario_file)
    script = tmp_path / "check.py"
    script.write_text(KRROOD_AGAINST_PLAIN_PYTHON)
    completed = subprocess.run(
        [sys.executable, str(script), str(scenario_file)], capture_output=True, text=True, timeout=900
    )
    assert completed.returncode == 0, completed.stderr[-3000:]
    report = json.loads(completed.stdout.strip().splitlines()[-1])
    assert report["steps"] == 6
    assert report["mismatches"] == []
    assert all(count > 0 for count in report["handouts"])
    assert all(count >= 20 for count in report["tickets"])


def graphdb_reachable() -> bool:
    try:
        return requests.get(f"{DEFAULT_GRAPHDB_URL}/rest/info/version", timeout=5).ok
    except requests.RequestException:
        return False


def run_driver(tmp_path: Path, variants: str, steps: int) -> dict:
    completed = subprocess.run(
        [sys.executable, str(DRIVER), "--steps", str(steps), "--seed", "5", "--variants", variants,
         "--results-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=4 * 3600,
    )
    assert completed.returncode == 0, completed.stderr[-3000:]
    return json.loads((tmp_path / "agent_loop.json").read_text())


@pytest.mark.skipif(
    os.environ.get("AGENT_LOOP_GRAPHDB_TESTS") != "1" or not graphdb_reachable(),
    reason="needs a GraphDB server and AGENT_LOOP_GRAPHDB_TESTS=1 (loading takes about 20 minutes)",
)
def test_graphdb_variants_decide_like_krrood(tmp_path):
    summary = run_driver(tmp_path, "krrood,graphdb,graphdb_push", steps=4)
    for variant in ("graphdb", "graphdb_push"):
        agreement = summary["variants"][variant]["agreement"]
        assert agreement["all_agree"], agreement["first_disagreements"]
    assert summary["variants"]["graphdb_push"]["setup"]["repository_reused"]


@pytest.mark.skipif(
    os.environ.get("AGENT_LOOP_REASONABLE_TESTS") != "1",
    reason="needs reasonable and AGENT_LOOP_REASONABLE_TESTS=1 (about 5 minutes)",
)
def test_reasonable_agrees_on_tickets_but_misses_property_chains(tmp_path):
    summary = run_driver(tmp_path, "krrood,reasonable", steps=3)
    agreement = summary["variants"]["reasonable"]["agreement"]
    assert agreement["equal_candidate_sets"] < agreement["steps"]
    for difference in agreement["first_disagreements"]:
        assert difference["tickets"]["only_in_reference"] == difference["tickets"]["only_in_variant"] == 0
        assert difference["handouts"]["only_in_variant"] == 0
        assert difference["handouts"]["only_in_reference"] > 0


def test_nemo_step_program_reads_the_perceived_facts_and_exports_only_the_answers():
    program = step_program(NEMO_RULES.read_text())
    assert program.count("@import ") == 2 and "perceived" in program
    assert [line for line in program.splitlines() if line.startswith("@export")] == [
        '@export handout :- csv{resource = "handout.csv"} .', '@export fan :- csv{resource = "fan.csv"} .']
    assert "prp-spo2" in program


@pytest.mark.skipif(
    shutil.which(os.environ.get("NEMO_BINARY", "nmo")) is None, reason="needs Nemo's nmo (NEMO_BINARY)"
)
def test_nemo_decides_like_krrood(tmp_path):
    summary = run_driver(tmp_path, "krrood,nemo", steps=3)
    agreement = summary["variants"]["nemo"]["agreement"]
    assert agreement["all_agree"], agreement["first_disagreements"]
