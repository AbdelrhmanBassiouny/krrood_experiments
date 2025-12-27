import os.path
import runpy


def pytest_sessionstart(session) -> None:
    """
    Generate the ORM at the start of the test run.
    """
    runpy.run_path(os.path.join("..", "scripts", "generate_orm.py"))
