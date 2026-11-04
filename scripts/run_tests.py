# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.58.0"]
# ///
"""Run every test in the repository in one process and fail any test over the time bar.

Usage: uv run scripts/run_tests.py

Finds every test_*.py beside a script, runs each file's tests in-process, and times each
test with its share of setup: a class's or module's setup counts against its first test.
Time the process spent waiting for a CPU is subtracted, so a busy machine cannot fail a
test. The bar lives in scripts/test-bar.json: the most one test may take and the most the
whole run may take. Exits 1 when a test fails or is over the bar, or the run is over its own.
"""

import importlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
BAR = json.loads((ROOT / "scripts" / "test-bar.json").read_text())


def cpu_wait_seconds():
    """Seconds this process's threads have waited on a run queue (Linux schedstat)."""
    total = 0
    for stat in Path("/proc/self/task").glob("*/schedstat"):
        total += int(stat.read_text().split()[1])
    return total / 1e9


class TimedResult(unittest.TextTestResult):
    """Charges each test the time since the previous test ended, so class setup counts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.times = []
        self.mark = self.clock()

    @staticmethod
    def clock():
        return time.perf_counter() - cpu_wait_seconds()

    def stopTest(self, test):
        now = self.clock()
        self.times.append((test.id(), now - self.mark))
        self.mark = now
        super().stopTest(test)


def test_files():
    return sorted(path for path in ROOT.glob("**/test_*.py")
                  if "node_modules" not in path.parts and "personal" not in path.parts
                  and "personal-archive" not in path.parts)


def main():
    started = TimedResult.clock()
    failures, slow, times = [], [], []
    for path in test_files():
        sys.path.insert(0, str(path.parent))
        try:
            module = importlib.import_module(path.stem)
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            result = TimedResult(io.StringIO(), descriptions=False, verbosity=0)
            suite.run(result)
        finally:
            sys.path.remove(str(path.parent))
        relative = path.relative_to(ROOT)
        for test, trace in result.failures + result.errors:
            failures.append(f"{relative}: {test.id()}\n{trace}")
        for test_id, seconds in result.times:
            times.append((seconds, f"{relative}::{test_id.split('.', 1)[1]}"))
    total = TimedResult.clock() - started
    slow = [(s, name) for s, name in times if s > BAR["per_test_seconds"]]

    for failure in failures:
        print(f"FAIL {failure}")
    times.sort(reverse=True)
    print(f"{len(times)} tests in {total:.2f} s; slowest:")
    for seconds, name in times[:5]:
        print(f"  {seconds:.3f} s  {name}")
    for seconds, name in slow:
        print(f"OVER THE BAR ({BAR['per_test_seconds']} s per test): {seconds:.3f} s {name}")
    if total > BAR["full_run_seconds"]:
        print(f"OVER THE BAR ({BAR['full_run_seconds']} s for the run): {total:.2f} s")
    if slow or total > BAR["full_run_seconds"]:
        print("A test over the bar is made fast or deleted: no raised limit, slow tag or skip.")
    return 1 if failures or slow or total > BAR["full_run_seconds"] else 0


if __name__ == "__main__":
    sys.exit(main())
