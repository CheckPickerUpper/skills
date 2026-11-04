"""Fail any test, or the whole run, over the bar in pytest.ini.

Each test is charged everything its run protocol does, so a class's setup counts
against its first test. Time the test thread spent waiting for a CPU is
subtracted, so a busy machine cannot fail a test.
"""

from pathlib import Path
import time

import pytest

TIMES = {}


def pytest_addoption(parser):
    parser.addini("per_test_seconds", "the most one test may take, its setup included")
    parser.addini("full_run_seconds", "the most the whole run may take")


def cpu_wait_seconds():
    """Seconds the test thread has waited on a run queue (Linux schedstat). Only this
    thread counts: other threads and processes wait in parallel, so their waits are
    not time the test lost."""
    try:
        return int(Path("/proc/thread-self/schedstat").read_text().split()[1]) / 1e9
    except OSError:
        return 0.0


def clock():
    return time.perf_counter() - cpu_wait_seconds()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    started = clock()
    yield
    TIMES[item.nodeid] = clock() - started


def pytest_sessionstart(session):
    session.started = clock()


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    per_test, full_run = float(config.getini("per_test_seconds")), float(config.getini("full_run_seconds"))
    total = clock() - session.started
    slow = sorted(((s, n) for n, s in TIMES.items() if s > per_test), reverse=True)
    lines = [f"{len(TIMES)} tests in {total:.2f} s; slowest:"]
    lines += [f"  {s:.3f} s  {n}" for s, n in sorted(((s, n) for n, s in TIMES.items()), reverse=True)[:5]]
    lines += [f"OVER THE BAR ({per_test} s per test): {s:.3f} s {n}" for s, n in slow]
    if total > full_run:
        lines.append(f"OVER THE BAR ({full_run} s for the run): {total:.2f} s")
    if slow or total > full_run:
        lines.append("A test over the bar is made fast or deleted: no raised limit, slow tag or skip.")
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
    reporter = config.pluginmanager.get_plugin("terminalreporter")
    for line in lines:
        reporter.write_line(line)
