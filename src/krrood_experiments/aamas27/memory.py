"""
Peak memory and wall-time measurement of a process tree.

A child command is started in a fresh process, and the resident set size (RSS) of the child and all of its
descendants (for example the Java process that owlready2 starts for Pellet) is sampled every
``interval_seconds``. The peak of the summed RSS is reported. The same sampler can watch an already running process
(for example the GraphDB server JVM) while some other action is performed.
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Callable, List, Optional, Dict, Any, Sequence

import psutil


def tree_rss_bytes(root: psutil.Process) -> int:
    """
    :param root: The root process.
    :return: The summed resident set size of the root process and all its descendants.
    """
    total = 0
    try:
        processes = [root] + root.children(recursive=True)
    except psutil.NoSuchProcess:
        return 0
    for process in processes:
        try:
            total += process.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return total


@dataclass
class RssSampler:
    """
    Samples the summed RSS of a process tree in a background thread.
    """

    process: psutil.Process
    """
    The root of the sampled process tree.
    """
    interval_seconds: float = 0.05
    """
    Sampling interval.
    """
    peak_bytes: int = 0
    """
    The highest summed RSS seen so far.
    """
    first_bytes: Optional[int] = None
    """
    The first sample, used as baseline for long-running servers.
    """
    samples: int = 0
    """
    The number of samples taken.
    """
    limit_bytes: Optional[int] = None
    """
    If set, the process tree is killed as soon as its summed RSS exceeds this value.
    """
    limit_exceeded: bool = False
    """
    Whether the process tree was killed because it exceeded :attr:`limit_bytes`.
    """
    _stop: threading.Event = field(default_factory=threading.Event, repr=False)
    _thread: Optional[threading.Thread] = field(default=None, repr=False)

    def _run(self) -> None:
        while not self._stop.is_set():
            rss = tree_rss_bytes(self.process)
            if self.first_bytes is None:
                self.first_bytes = rss
            self.peak_bytes = max(self.peak_bytes, rss)
            self.samples += 1
            if self.limit_bytes is not None and rss > self.limit_bytes:
                self.limit_exceeded = True
                kill_tree(self.process.pid)
                return
            self._stop.wait(self.interval_seconds)

    def start(self) -> RssSampler:
        """
        Start sampling in a daemon thread.
        """
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        """
        Stop sampling.
        """
        self._stop.set()
        if self._thread is not None:
            self._thread.join()


@dataclass
class MeasuredRun:
    """
    The outcome of a measured subprocess run.
    """

    command: List[str]
    """
    The executed command.
    """
    wall_seconds: float
    """
    Wall-clock time of the whole subprocess, including interpreter start-up and imports.
    """
    peak_rss_bytes: int
    """
    Peak summed RSS of the process tree.
    """
    return_code: Optional[int]
    """
    The return code, or None when the process was killed because of the timeout.
    """
    timed_out: bool
    """
    Whether the process exceeded the timeout and was killed.
    """
    memory_limit_exceeded: bool
    """
    Whether the process tree exceeded the memory limit and was killed.
    """
    samples: int
    """
    The number of RSS samples taken.
    """
    worker_result: Optional[Dict[str, Any]] = None
    """
    The JSON object printed by the worker on its last stdout line that starts with ``RESULT_JSON``.
    """
    stderr_tail: str = ""
    """
    The last lines of the standard error stream, for diagnosing failures.
    """

    @property
    def peak_rss_mib(self) -> float:
        return self.peak_rss_bytes / 2**20

    def to_json(self) -> Dict[str, Any]:
        result = asdict(self)
        result["peak_rss_mib"] = self.peak_rss_mib
        return result


RESULT_MARKER = "RESULT_JSON "
"""
Prefix of the stdout line on which worker processes report their internal measurements.
"""


def print_worker_result(result: Dict[str, Any]) -> None:
    """
    Report internal measurements from a worker process to the parent.

    :param result: A JSON-serialisable mapping.
    """
    print(RESULT_MARKER + json.dumps(result), flush=True)


def run_measured(
    command: Sequence[str],
    timeout_seconds: Optional[float] = None,
    interval_seconds: float = 0.05,
    environment: Optional[Dict[str, str]] = None,
    working_directory: Optional[str] = None,
    memory_limit_bytes: Optional[int] = None,
) -> MeasuredRun:
    """
    Run a command in a fresh process and measure its wall time and the peak RSS of its process tree.

    :param command: The command to execute.
    :param timeout_seconds: Kill the process tree after this many seconds.
    :param interval_seconds: RSS sampling interval.
    :param environment: Environment variables for the child process.
    :param working_directory: Working directory for the child process.
    :param memory_limit_bytes: Kill the process tree when its summed RSS exceeds this value.
    :return: The measured run.
    """
    start = time.perf_counter()
    child = subprocess.Popen(
        list(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        cwd=working_directory,
    )
    sampler = RssSampler(
        psutil.Process(child.pid), interval_seconds, limit_bytes=memory_limit_bytes
    ).start()
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_tree(child.pid)
        stdout, stderr = child.communicate()
    wall_seconds = time.perf_counter() - start
    sampler.stop()
    worker_result = None
    for line in stdout.splitlines():
        if line.startswith(RESULT_MARKER):
            worker_result = json.loads(line[len(RESULT_MARKER) :])
    return MeasuredRun(
        command=list(command),
        wall_seconds=wall_seconds,
        peak_rss_bytes=sampler.peak_bytes,
        return_code=None if timed_out else child.returncode,
        timed_out=timed_out,
        memory_limit_exceeded=sampler.limit_exceeded,
        samples=sampler.samples,
        worker_result=worker_result,
        stderr_tail="\n".join(stderr.splitlines()[-30:]),
    )


def kill_tree(pid: int) -> None:
    """
    Kill a process and all of its descendants.

    :param pid: The root process identifier.
    """
    try:
        root = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    processes = root.children(recursive=True) + [root]
    for process in processes:
        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(processes, timeout=30)


@dataclass
class ServerMeasurement:
    """
    Memory of a long-running server process observed while an action is performed.
    """

    wall_seconds: float
    """
    Wall-clock time of the action.
    """
    rss_before_bytes: int
    """
    RSS of the server before the action.
    """
    peak_rss_bytes: int
    """
    Peak RSS of the server during the action.
    """
    rss_after_bytes: int
    """
    RSS of the server after the action.
    """

    def to_json(self) -> Dict[str, Any]:
        result = asdict(self)
        result["peak_rss_mib"] = self.peak_rss_bytes / 2**20
        result["peak_minus_before_mib"] = (
            self.peak_rss_bytes - self.rss_before_bytes
        ) / 2**20
        return result


def measure_server_during(
    server: psutil.Process, action: Callable[[], Any], interval_seconds: float = 0.05
) -> tuple[ServerMeasurement, Any]:
    """
    Observe the RSS of a server process while executing an action in the current process.

    :param server: The server process.
    :param action: The action, for example an HTTP upload to the server.
    :param interval_seconds: RSS sampling interval.
    :return: The measurement and the return value of the action.
    """
    before = tree_rss_bytes(server)
    sampler = RssSampler(server, interval_seconds).start()
    start = time.perf_counter()
    value = action()
    wall_seconds = time.perf_counter() - start
    sampler.stop()
    return (
        ServerMeasurement(
            wall_seconds=wall_seconds,
            rss_before_bytes=before,
            peak_rss_bytes=sampler.peak_bytes,
            rss_after_bytes=tree_rss_bytes(server),
        ),
        value,
    )
