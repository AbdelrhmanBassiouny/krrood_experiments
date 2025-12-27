import os.path
import runpy


def pytest_sessionstart(session) -> None:
    """
    Generate the ORM at the start of the test run.
    """

    this_file_path = os.path.abspath(__file__)
    runpy.run_path(
        os.path.join(this_file_path, "..", "..", "scripts", "generate_orm.py"),
        run_name="__main__",
    )
