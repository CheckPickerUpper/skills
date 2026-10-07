"""Behavioral tests at TOML, command-line, file and Unix WebSocket boundaries."""

import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from websockets.asyncio.server import unix_serve

import conductor_config as config
import usage_readers as readers

SCRIPT = Path(config.__file__).resolve()
NOW = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
MODES = {
    "ignore": {},
    "finish-in-flight": {"at_percent": 85},
    "stop-at-commit": {"at_percent": 90},
    "finish-in-flight-then-stop": {"wind_down_at_percent": 80, "stop_at_percent": 95},
}


def raw_policy(mode):
    return {"mode": mode, **MODES[mode]}


def policy(kind, mode):
    return config.usage_policy(Path("test.toml"), kind, raw_policy(mode))


def cli(root, *arguments, python_options=()):
    return subprocess.run(
        [sys.executable, *python_options, str(SCRIPT), *arguments], cwd=root,
        env={**os.environ, "HOME": str(root), "XDG_CONFIG_HOME": str(root / "config"),
             "XDG_STATE_HOME": str(root / "state")},
        capture_output=True, text=True, timeout=10,
    )


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="usage-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / config.CONFIG_FILE

    def reject(self, toml, kind, key):
        self.path.write_text(toml)
        with self.assertRaises(SystemExit) as raised:
            config.read_settings(self.path)
        error = str(raised.exception)
        self.assertIn(str(self.path), error)
        self.assertIn(kind, error)
        self.assertIn(key, error)
        self.assertIn("allowed", error)

    def test_unknown_kind_is_rejected(self):
        self.reject('[usage.gemini]\nmode="ignore"', "gemini", "gemini")

    def test_unknown_key_is_rejected(self):
        self.reject('[usage.pi]\nmode="ignore"\nextra=1', "pi", "extra")

    def test_missing_mode_is_rejected(self):
        self.reject('[usage.pi]', "pi", "mode")

    def test_unknown_mode_is_rejected(self):
        self.reject('[usage.pi]\nmode="hard-stop"', "pi", "mode")

    def test_non_string_mode_is_rejected(self):
        self.reject('[usage.pi]\nmode=3', "pi", "mode")

    def test_each_mode_rejects_keys_it_does_not_allow(self):
        for mode, thresholds in MODES.items():
            forbidden = {"at_percent", "wind_down_at_percent", "stop_at_percent"} - thresholds.keys()
            for key in forbidden:
                with self.subTest(mode=mode, key=key):
                    rows = [f'[usage.claude]\nmode="{mode}"']
                    rows += [f"{name}={value}" for name, value in thresholds.items()]
                    self.reject("\n".join([*rows, f"{key}=99"]), "claude", key)

    def test_each_mode_requires_its_thresholds(self):
        for mode, thresholds in MODES.items():
            for key in thresholds:
                with self.subTest(mode=mode, key=key):
                    rows = [f'[usage.claude]\nmode="{mode}"']
                    rows += [f"{name}={value}" for name, value in thresholds.items() if name != key]
                    self.reject("\n".join(rows), "claude", key)

    def test_percent_requires_an_integer(self):
        for value in ('85.0', '"85"', '[85]'):
            with self.subTest(value=value):
                self.reject(f'[usage.claude]\nmode="finish-in-flight"\nat_percent={value}', "claude", "at_percent")

    def test_percent_rejects_bool(self):
        self.reject('[usage.claude]\nmode="finish-in-flight"\nat_percent=true', "claude", "at_percent")

    def test_percent_rejects_out_of_range(self):
        for value in (0, 101):
            with self.subTest(value=value):
                self.reject(f'[usage.claude]\nmode="finish-in-flight"\nat_percent={value}', "claude", "at_percent")

    def test_equal_thresholds_are_rejected(self):
        self.reject('[usage.claude]\nmode="finish-in-flight-then-stop"\nwind_down_at_percent=85\nstop_at_percent=85', "claude", "wind_down_at_percent")

    def test_reversed_thresholds_are_rejected(self):
        self.reject('[usage.claude]\nmode="finish-in-flight-then-stop"\nwind_down_at_percent=95\nstop_at_percent=85', "claude", "wind_down_at_percent")

    def test_usage_tables_reject_spend_credits(self):
        for kind in ("codex", "claude", "pi"):
            for mode in MODES if kind != "pi" else ("ignore",):
                with self.subTest(kind=kind, mode=mode):
                    rows = [f'[usage.{kind}]', f'mode="{mode}"', 'spend_credits=true']
                    rows += [f'{key}={value}' for key, value in MODES[mode].items()]
                    self.reject("\n".join(rows), kind, "spend_credits")

    def test_pi_rejects_modes_without_a_reader(self):
        for mode in MODES:
            if mode != "ignore":
                with self.subTest(mode=mode):
                    rows = [f'[usage.pi]\nmode="{mode}"']
                    rows += [f'{key}={value}' for key, value in MODES[mode].items()]
                    self.reject("\n".join(rows), "pi", "mode")

    def test_global_credits_requires_bool(self):
        for value in ('1', '"true"'):
            self.reject(f'[credits]\ncodex={value}', "credits", "codex")

    def test_global_credits_rejects_unknown_keys(self):
        self.reject('[credits]\nclaude=true', "credits", "claude")

    def test_credits_requires_table(self):
        self.reject('credits=true', "credits", "credits")

    def test_project_credits_is_rejected_by_read_and_write(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        project = self.root / ".checkpickerupper" / config.CONFIG_FILE
        project.parent.mkdir()
        project.write_text('[credits]\ncodex=true')
        result = cli(self.root, "show")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(project), result.stderr)
        self.assertIn("credits", result.stderr)
        project.unlink()
        result = cli(self.root, "write", "--scope", "project", "--codex-spend-credits", "true")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(project), result.stderr)
        self.assertIn("credits", result.stderr)
        self.assertFalse(project.exists())

    def test_finish_in_flight_requires_credit_answer_only_for_show(self):
        result = cli(self.root, "write", "--scope", "global", "--max-implementers", "2", "--merge", "conductor", "--review-skills", "", "--usage-kind", "codex", "--usage-mode", "finish-in-flight", "--at-percent", "85")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(cli(self.root, "show").returncode, 0)
        result = cli(self.root, "show", "--kind", "codex")
        self.assertEqual(result.returncode, 3)
        self.assertIn("credits.codex", result.stderr)
        for answer in ("true", "false"):
            result = cli(self.root, "write", "--scope", "global", "--codex-spend-credits", answer)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(cli(self.root, "show", "--kind", "codex").returncode, 0)
            settings = config.read_settings(self.root / "config/checkpickerupper" / config.CONFIG_FILE)
            self.assertEqual(settings["credits"], {"codex": answer == "true"})
        for mode in ("ignore", "stop-at-commit", "finish-in-flight-then-stop"):
            args = ["write", "--scope", "global", "--usage-kind", "codex", "--usage-mode", mode]
            for key, value in MODES[mode].items():
                args += ["--" + key.replace("_", "-"), str(value)]
            self.assertEqual(cli(self.root, *args).returncode, 0)
            target = self.root / "config/checkpickerupper" / config.CONFIG_FILE
            settings = config.read_settings(target)
            settings.pop("credits", None)
            target.write_text(config.render(settings))
            self.assertEqual(cli(self.root, "show", "--kind", "codex").returncode, 0)

    def test_bad_config_encoding_is_a_named_error(self):
        self.path.write_bytes(b"# \xff")
        with self.assertRaises(SystemExit) as raised:
            config.read_settings(self.path)
        self.assertIn(str(self.path), str(raised.exception))
        self.assertIn("config error UnicodeDecodeError", str(raised.exception))

    def test_usage_requires_table(self):
        self.reject('usage="ignore"', "<kind>", "usage")

    def test_kind_requires_table(self):
        self.reject('[usage]\nclaude="ignore"', "claude", "claude")

    def test_every_mode_and_kind_writes_and_reads_back(self):
        for kind in ("codex", "claude", "pi"):
            for mode in MODES if kind != "pi" else ("ignore",):
                with self.subTest(kind=kind, mode=mode):
                    expected = raw_policy(mode)
                    args = ["write", "--scope", "global", "--usage-kind", kind, "--usage-mode", mode]
                    for key, value in expected.items():
                        if key != "mode":
                            args += [f"--{key.replace('_', '-')}", str(value).lower()]
                    result = cli(self.root, *args)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    settings = config.read_settings(self.root / "config/checkpickerupper" / config.CONFIG_FILE)
                    self.assertEqual(config.policy_values(settings["usage"][kind]), expected)

    def test_invalid_write_preserves_existing_file(self):
        target = self.root / "config/checkpickerupper" / config.CONFIG_FILE
        target.parent.mkdir(parents=True)
        original = '[usage.pi]\nmode="ignore"\n'
        target.write_text(original)
        result = cli(self.root, "write", "--scope", "global", "--usage-kind", "pi", "--usage-mode", "ignore", "--at-percent", "85")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at_percent", result.stderr)
        self.assertEqual(target.read_text(), original)

    def test_usage_flags_require_kind(self):
        result = cli(self.root, "write", "--scope", "global", "--max-implementers", "1", "--at-percent", "85")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--usage-kind", result.stderr)

    def test_percent_endpoints_are_accepted(self):
        for value in (1, 100):
            self.path.write_text(f'[usage.claude]\nmode="stop-at-commit"\nat_percent={value}')
            self.assertEqual(config.read_settings(self.path)["usage"]["claude"].at_percent, value)

    def test_project_usage_replaces_only_its_kind_and_show_tracks_source(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        global_path = self.root / "config/checkpickerupper" / config.CONFIG_FILE
        global_path.parent.mkdir(parents=True)
        global_path.write_text('max_implementers=2\nmerge="conductor"\nreview_skills=[]\n[usage.codex]\nmode="finish-in-flight-then-stop"\nwind_down_at_percent=80\nstop_at_percent=95\n[usage.claude]\nmode="stop-at-commit"\nat_percent=85')
        project_path = self.root / ".checkpickerupper" / config.CONFIG_FILE
        project_path.parent.mkdir()
        project_path.write_text('[usage.codex]\nmode="ignore"')
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root / "config")}):
            resolved, _, _ = config.resolve(str(self.root))
        self.assertEqual({kind: config.policy_values(saved) for kind, saved in resolved["usage"].items()}, {"codex": {"mode": "ignore"}, "claude": {"mode": "stop-at-commit", "at_percent": 85}})
        result = cli(self.root, "show", "--kind", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        shown = json.loads(result.stdout)
        self.assertEqual(shown["usage"]["codex"], {"value": {"mode": "ignore"}, "from": str(project_path)})
        self.assertEqual(shown["max_implementers"]["value"], 2)
        self.assertEqual(cli(self.root, "show").returncode, 0)
        self.assertEqual(cli(self.root, "show", "--kind", "pi").returncode, 3)
        project_path.write_text('[usage.codex]\nmode="ignore"\nat_percent=85')
        self.assertIn("at_percent", cli(self.root, "show").stderr)
        project_path.write_text('[usage.codex]\nmode="ignore"')
        global_path.write_text('[usage.codex]\nmode="ignore"\nat_percent=85')
        self.assertIn("at_percent", cli(self.root, "show").stderr)

    def test_missing_top_level_settings_still_exit_three(self):
        result = cli(self.root, "show")
        self.assertEqual(result.returncode, 3)
        self.assertIn("max_implementers, merge, review_skills", result.stderr)

    def test_ignore_never_reads_a_missing_socket_or_claude_file(self):
        for kind in ("codex", "claude", "pi"):
            result = cli(self.root, "write", "--scope", "global", "--usage-kind", kind, "--usage-mode", "ignore")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((self.root / ".codex/app-server-control/app-server-control.sock").exists())
            # An audit hook rejects even an attempted socket or usage-file read.
            program = """
import runpy, sys
from pathlib import Path
script = sys.argv[1]
sys.argv = [script, 'usage', '--kind', sys.argv[2]]
def audit(event, arguments):
    if event == 'socket.connect':
        raise RuntimeError('reader attempted a connection')
    if event == 'open' and str(arguments[0]).endswith('claude.json'):
        raise RuntimeError('reader attempted the Claude usage file')
sys.addaudithook(audit)
runpy.run_path(script, run_name='__main__')
"""
            result = subprocess.run([sys.executable, "-c", program, str(SCRIPT), kind], cwd=SCRIPT.parent,
                                    env={**os.environ, "HOME": str(self.root), "XDG_CONFIG_HOME": str(self.root / "config"), "XDG_STATE_HOME": str(self.root / "state")},
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"kind": kind, "mode": "ignore", "used_percent": None, "window_minutes": None, "resets_at": None, "state": "normal", "reason": "usage ignored by policy"})



class StateTest(unittest.TestCase):
    def state(self, kind, mode, used, credits=False, spend=True):
        configured = policy(kind, mode)
        reading = readers.Reading(used, 300, NOW.isoformat(), "usable" if credits else "unusable")
        return config.usage_state(kind, configured, reading, spend).state

    def test_thresholds_before_at_and_after(self):
        for kind in ("codex", "claude"):
            for mode, points in (
                ("ignore", [(0, "normal"), (99, "normal")]),
                ("finish-in-flight", [(84, "normal"), (85, "wind-down"), (86, "wind-down")]),
                ("stop-at-commit", [(89, "normal"), (90, "stop"), (91, "stop")]),
                ("finish-in-flight-then-stop", [(79, "normal"), (80, "wind-down"), (81, "wind-down"), (94, "wind-down"), (95, "stop"), (96, "stop")]),
            ):
                for used, expected in points:
                    with self.subTest(kind=kind, mode=mode, used=used):
                        self.assertEqual(self.state(kind, mode, used), expected)

    def test_only_finish_in_flight_can_continue_on_opted_in_usable_credits(self):
        for mode in MODES:
            for kind in ("codex", "claude"):
                with self.subTest(kind=kind, mode=mode):
                    expected = "normal" if mode == "ignore" else "exhausted"
                    self.assertEqual(self.state(kind, mode, 100), expected)
            expected = "normal" if mode == "ignore" else "exhausted"
            self.assertEqual(self.state("codex", mode, 100, credits=True, spend=False), expected)
            expected = {"ignore": "normal", "finish-in-flight": "wind-down", "stop-at-commit": "exhausted", "finish-in-flight-then-stop": "exhausted"}[mode]
            self.assertEqual(self.state("codex", mode, 100, credits=True), expected)

    def test_unavailable_is_normal_only_for_ignore(self):
        for mode in MODES:
            row = config.usage_state("claude", policy("claude", mode), readers.Unavailable("no reader"))
            self.assertEqual(row.state, "normal" if mode == "ignore" else "unknown")
            self.assertEqual(row.reason, "usage ignored by policy" if mode == "ignore" else "no reader")
            self.assertIsNone(row.used_percent)

    def test_missing_policy_is_unknown(self):
        row = config.usage_state("codex", None, readers.Reading(50, 300, None))
        self.assertEqual(row.state, "unknown")
        self.assertIn("usage.codex", row.reason)
        failed = config.usage_state("codex", None, readers.Unavailable("socket missing"))
        self.assertEqual(failed.state, "unknown")
        self.assertIn("socket missing", failed.reason)


class ClaudeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="usage-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "state/dotfiles/usage/claude.json"
        self.path.parent.mkdir(parents=True)

    def save(self, age=0, limits=None):
        self.path.write_text(json.dumps({"received_at": (NOW - timedelta(seconds=age)).isoformat(), "rate_limits": limits or {"five_hour": {"used_percentage": 40}, "seven_day": {"used_percentage": 90, "resets_at": 1791979200}}}))

    def test_highest_claude_window_carries_its_reset_and_duration(self):
        self.save()
        self.assertEqual(readers.read_claude(self.path, NOW), readers.Reading(90, 10080, "2026-10-14T12:00:00+00:00"))
        self.save(limits={"five_hour": {"used_percentage": 91}, "seven_day": None})
        self.assertEqual(readers.read_claude(self.path, NOW), readers.Reading(91, 300, None))

    def test_ten_minutes_is_available_but_older_is_unknown(self):
        self.save(age=600)
        self.assertIsInstance(readers.read_claude(self.path, NOW), readers.Reading)
        self.save(age=601)
        row = config.usage_state("claude", policy("claude", "finish-in-flight"), readers.read_claude(self.path, NOW))
        self.assertEqual(row.state, "unknown")
        self.assertIn("stale", row.reason)

    def test_bad_claude_data_is_unavailable_with_cause(self):
        for value, cause in (("{", "JSONDecodeError"), ('[]', "object"), ('{"received_at":"bad"}', "isoformat")):
            with self.subTest(value=value):
                self.path.write_text(value)
                reading = readers.read_claude(self.path, NOW)
                self.assertIsInstance(reading, readers.Unavailable)
                self.assertIn(cause, reading.reason)
        self.path.unlink()
        self.assertIn("FileNotFoundError", readers.read_claude(self.path, NOW).reason)

    def test_claude_cli_reads_xdg_state_file(self):
        self.path.write_text(json.dumps({"received_at": datetime.now(timezone.utc).isoformat(), "rate_limits": {"five_hour": {"used_percentage": 87}}}))
        cli(self.root, "write", "--scope", "global", "--usage-kind", "claude", "--usage-mode", "finish-in-flight", "--at-percent", "85")
        result = cli(self.root, "usage", "--kind", "claude")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "wind-down")


class CodexSocketTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="u-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.socket = self.root / "s"
        self.requests = []
        self.behavior = "normal"
        self.result = {"ordinaryUsageAllowed": True, "rateLimits": {
            "primary": {"usedPercent": 40, "windowDurationMins": 300, "resetsAt": 1791948537},
            "secondary": {"usedPercent": 97, "windowDurationMins": 10080, "resetsAt": 1791948538},
            "credits": {"hasCredits": True, "unlimited": False},
        }}

    async def handler(self, connection):
        initialize = json.loads(await connection.recv())
        self.requests.append(initialize)
        if self.behavior == "closed":
            # A slow close must remain distinct from the old 0.3s timeout.
            await asyncio.sleep(0.4)
            await connection.close()
            return
        if self.behavior == "timeout":
            await connection.wait_closed()
            return
        if self.behavior == "initialize-error":
            await connection.send(json.dumps({"id": 1, "error": {"message": "initialize refused"}}))
            return
        await connection.send(json.dumps({"method": "notice", "params": {}}))
        await connection.send(json.dumps({"id": 1, "result": {}}))
        self.requests.append(json.loads(await connection.recv()))
        request = json.loads(await connection.recv())
        self.requests.append(request)
        if self.behavior == "malformed":
            await connection.send("{")
        elif self.behavior == "error":
            await connection.send(json.dumps({"id": request["id"], "error": {"message": "quota read refused"}}))
        else:
            await connection.send(json.dumps({"id": request["id"], "result": self.result}))

    async def read(self, timeout_seconds=5):
        async with unix_serve(self.handler, str(self.socket)):
            return await readers.read_codex(self.socket, timeout_seconds=timeout_seconds)

    async def test_real_unix_server_protocol_and_highest_window(self):
        reading = await self.read()
        self.assertEqual(reading, readers.Reading(97, 10080, "2026-10-14T03:28:58+00:00", "usable"))
        self.assertEqual(self.requests, [
            {"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "conductor-mode", "version": "1"}}},
            {"method": "initialized"},
            {"id": 2, "method": "account/rateLimits/read", "params": {}},
        ])

    async def test_null_window_and_unlimited_credits_are_usable(self):
        self.result["rateLimits"]["secondary"] = None
        self.result["rateLimits"]["credits"] = {"hasCredits": False, "unlimited": True}
        reading = await self.read()
        self.assertEqual(reading.used_percent, 40)
        self.assertEqual(reading.credit_status, "usable")

    async def test_ordinary_permission_unavailable_is_unknown_even_with_credits(self):
        for value in (None, "missing"):
            with self.subTest(value=value):
                if value == "missing":
                    self.result.pop("ordinaryUsageAllowed")
                else:
                    self.result["ordinaryUsageAllowed"] = value
                reading = await self.read()
                row = config.usage_state("codex", policy("codex", "finish-in-flight"), reading, True)
                self.assertEqual(row.state, "unknown")
                self.assertIn("ordinaryUsageAllowed", row.reason)

    async def test_ordinary_permission_false_blocks_below_threshold(self):
        self.result["ordinaryUsageAllowed"] = False
        self.result["rateLimits"]["primary"]["usedPercent"] = 10
        self.result["rateLimits"]["secondary"] = None
        reading = await self.read()
        self.assertEqual(config.usage_state("codex", policy("codex", "finish-in-flight"), reading, False).state, "exhausted")
        self.assertEqual(config.usage_state("codex", policy("codex", "finish-in-flight"), reading, True).state, "wind-down")
        self.assertEqual(config.usage_state("codex", policy("codex", "stop-at-commit"), reading, True).state, "exhausted")

    async def test_reached_type_blocks_even_when_permission_is_true(self):
        self.result["rateLimits"]["rateLimitReachedType"] = "rate_limit_reached"
        self.result["rateLimits"]["primary"]["usedPercent"] = 10
        self.result["rateLimits"]["secondary"] = None
        reading = await self.read()
        self.assertEqual(config.usage_state("codex", policy("codex", "finish-in-flight"), reading, False).state, "exhausted")
        self.assertEqual(config.usage_state("codex", policy("codex", "finish-in-flight"), reading, True).state, "wind-down")

    async def test_spend_control_prevents_continuation_even_with_credits(self):
        self.result["rateLimits"]["secondary"]["usedPercent"] = 100
        self.result["rateLimits"]["spendControlReached"] = True
        reading = await self.read()
        row = config.usage_state("codex", policy("codex", "finish-in-flight"), reading, True)
        self.assertEqual(row.state, "exhausted")
        self.assertIn("spendControlReached", row.reason)
        for value in (False, None):
            self.result["rateLimits"]["spendControlReached"] = value
            reading = await self.read()
            self.assertEqual(config.usage_state("codex", policy("codex", "finish-in-flight"), reading, True).state, "wind-down")

    async def test_governing_bucket_ignores_per_limit_buckets(self):
        self.result["rateLimits"]["primary"]["usedPercent"] = 10
        self.result["rateLimits"]["secondary"] = None
        self.result["rateLimitsByLimitId"] = {"other": {"primary": {"usedPercent": 100}}}
        reading = await self.read()
        self.assertEqual(reading.used_percent, 10)
        self.assertEqual(config.usage_state("codex", policy("codex", "finish-in-flight"), reading, False).state, "normal")

    async def test_null_or_missing_credits_are_unusable(self):
        for value in (None, "missing"):
            with self.subTest(value=value):
                if value == "missing":
                    self.result["rateLimits"].pop("credits")
                else:
                    self.result["rateLimits"]["credits"] = value
                reading = await self.read()
                self.assertIsInstance(reading, readers.Reading)
                self.assertEqual(reading.credit_status, "unusable")

    async def test_null_window_metadata_passes_through(self):
        self.result["rateLimits"]["secondary"]["windowDurationMins"] = None
        self.result["rateLimits"]["secondary"]["resetsAt"] = None
        reading = await self.read()
        self.assertIsInstance(reading, readers.Reading)
        self.assertEqual(reading.used_percent, 97)
        self.assertIsNone(reading.window_minutes)
        self.assertIsNone(reading.resets_at)

    async def test_global_credit_choice_and_project_policy_continue_together(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        result = await asyncio.to_thread(cli, self.root, "write", "--scope", "global", "--codex-spend-credits", "true", "--usage-kind", "codex", "--usage-mode", "ignore")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = await asyncio.to_thread(cli, self.root, "write", "--scope", "project", "--usage-kind", "codex", "--usage-mode", "finish-in-flight", "--at-percent", "85")
        self.assertEqual(result.returncode, 0, result.stderr)
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root / "config")}):
            settings, _, _ = config.resolve(str(self.root))
        self.assertEqual(config.policy_values(settings["usage"]["codex"]), {"mode": "finish-in-flight", "at_percent": 85})
        self.assertEqual(settings["credits"], {"codex": True})
        self.result["rateLimits"]["secondary"]["usedPercent"] = 100
        reading = await self.read()
        row = config.usage_state("codex", settings["usage"]["codex"], reading, settings["credits"]["codex"])
        self.assertEqual(row.state, "wind-down")

    async def test_closed_socket_is_unknown(self):
        self.behavior = "closed"
        row = config.usage_state("codex", policy("codex", "finish-in-flight"), await self.read())
        self.assertEqual(row.state, "unknown")
        self.assertIn("ConnectionClosed", row.reason)

    async def test_missing_socket_is_unknown(self):
        row = config.usage_state("codex", policy("codex", "finish-in-flight"), await readers.read_codex(self.socket))
        self.assertEqual(row.state, "unknown")
        self.assertIn("FileNotFoundError", row.reason)

    async def test_timeout_is_unknown(self):
        self.behavior = "timeout"
        reading = await self.read(timeout_seconds=0.3)
        self.assertIsInstance(reading, readers.Unavailable)
        self.assertIn("timeout", reading.reason)

    async def test_error_responses_and_malformed_json_are_unknown(self):
        for behavior, cause in (("error", "quota read refused"), ("initialize-error", "initialize refused"), ("malformed", "JSONDecodeError")):
            with self.subTest(behavior=behavior):
                self.behavior = behavior
                reading = await self.read()
                row = config.usage_state("codex", policy("codex", "stop-at-commit"), reading)
                self.assertEqual(row.state, "unknown")
                self.assertIn(cause, row.reason)

    async def test_malformed_rate_limits_are_unavailable(self):
        for key, value, cause in (("primary", [], "primary"), ("credits", {}, "credits"), ("secondary", {"usedPercent": True}, "usedPercent")):
            with self.subTest(key=key):
                original = self.result["rateLimits"][key]
                self.result["rateLimits"][key] = value
                reading = await self.read()
                self.assertIsInstance(reading, readers.Unavailable)
                self.assertIn(cause, reading.reason)
                self.result["rateLimits"][key] = original

    async def test_cli_missing_websockets_is_unknown(self):
        result = await asyncio.to_thread(cli, self.root, "write", "--scope", "global", "--usage-kind", "codex", "--usage-mode", "finish-in-flight", "--at-percent", "85", "--codex-spend-credits", "true")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = await asyncio.to_thread(cli, self.root, "usage", "--kind", "codex", python_options=("-S",))
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)
        self.assertEqual(row["state"], "unknown")
        self.assertIn("websockets library unavailable", row["reason"])


if __name__ == "__main__":
    unittest.main()
