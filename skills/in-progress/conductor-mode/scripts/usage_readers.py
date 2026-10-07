"""Decode live agent usage at the Unix WebSocket and statusline-file boundaries."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Literal

READ_TIMEOUT_SECONDS = 5
CLAUDE_MAX_AGE_SECONDS = 600


@dataclass(frozen=True)
class Reading:
    used_percent: float
    window_minutes: int | None
    resets_at: str | None
    credit_status: Literal["usable", "unusable", "spend-control-reached"] = "unusable"
    ordinary_usage: Literal["allowed", "blocked"] = "allowed"


@dataclass(frozen=True)
class Unavailable:
    reason: str


def mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object")
    return value


def percentage(value: object, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError(f"{label} must be a number in 0..100")
    return float(value)


def iso_time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO 8601 timestamp")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return parsed


def epoch_time(value: object, label: str) -> str:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label} must be epoch seconds")
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def codex_reading(result: object) -> Reading:
    response = mapping(result, "result")
    ordinary = response.get("ordinaryUsageAllowed")
    if type(ordinary) is not bool:
        raise ValueError("ordinaryUsageAllowed is unavailable or is not a bool")
    # rateLimits is the account's governing bucket; rateLimitsByLimitId is not.
    limits = mapping(response.get("rateLimits"), "rateLimits")
    reached = limits.get("rateLimitReachedType")
    if reached is not None and not isinstance(reached, str):
        raise ValueError("rateLimitReachedType must be a string or null")
    spend_control = limits.get("spendControlReached")
    if spend_control is not None and type(spend_control) is not bool:
        raise ValueError("spendControlReached must be a bool or null")
    windows = [mapping(limits[key], key) for key in ("primary", "secondary") if limits.get(key) is not None]
    if not windows:
        raise ValueError("rateLimits has no primary or secondary window")
    readings = []
    for window in windows:
        used = percentage(window.get("usedPercent"), "usedPercent")
        minutes = window.get("windowDurationMins")
        if minutes is not None and (type(minutes) is not int or minutes <= 0):
            raise ValueError("windowDurationMins must be a positive int or null")
        reset = window.get("resetsAt")
        readings.append(Reading(used, minutes, epoch_time(reset, "resetsAt") if reset is not None else None))
    credit_status: Literal["usable", "unusable", "spend-control-reached"] = "unusable"
    if limits.get("credits") is not None:
        credits = mapping(limits["credits"], "credits")
        if any(type(credits.get(key)) is not bool for key in ("hasCredits", "unlimited")):
            raise ValueError("credits.hasCredits and credits.unlimited must be bools")
        if credits["hasCredits"] or credits["unlimited"]:
            credit_status = "usable"
    if spend_control is True:
        credit_status = "spend-control-reached"
    highest = max(readings, key=lambda reading: reading.used_percent)
    return Reading(highest.used_percent, highest.window_minutes, highest.resets_at,
credit_status, "blocked" if ordinary is False or reached is not None else "allowed")


async def read_codex(socket_path: Path, timeout_seconds: float = READ_TIMEOUT_SECONDS) -> Reading | Unavailable:
    try:
        from websockets.asyncio.client import unix_connect
        from websockets.exceptions import WebSocketException
    except ImportError as error:
        return Unavailable(f"websockets library unavailable: {error}")
    try:
        async with asyncio.timeout(timeout_seconds):
            async with unix_connect(str(socket_path), open_timeout=timeout_seconds, close_timeout=timeout_seconds) as connection:
                await connection.send(json.dumps({"id": 1, "method": "initialize", "params": {
                    "clientInfo": {"name": "conductor-mode", "version": "1"}}}))
                for request_id in (1, 2):
                    while True:
                        reply = mapping(json.loads(await connection.recv()), "JSON-RPC response")
                        if reply.get("id") == request_id:
                            break
                    if "error" in reply:
                        raise ValueError(f"{('initialize' if request_id == 1 else 'account/rateLimits/read')} error response: {reply['error']}")
                    if "result" not in reply:
                        raise ValueError("JSON-RPC response missing result")
                    if request_id == 1:
                        await connection.send(json.dumps({"method": "initialized"}))
                        await connection.send(json.dumps({"id": 2, "method": "account/rateLimits/read", "params": {}}))
                return codex_reading(reply["result"])
    except TimeoutError:
        return Unavailable(f"Codex socket {socket_path}: timeout after {timeout_seconds}s")
    except (OSError, WebSocketException, ValueError, OverflowError) as error:
        return Unavailable(f"Codex socket {socket_path}: {type(error).__name__}: {error}")


def read_claude(path: Path, now: datetime) -> Reading | Unavailable:
    try:
        with path.open() as handle:
            data = mapping(json.load(handle), "Claude usage")
        received = iso_time(data.get("received_at"), "received_at")
        age = (now - received).total_seconds()
        if age > CLAUDE_MAX_AGE_SECONDS:
            return Unavailable(f"Claude usage {path}: stale reading ({int(age)} seconds old)")
        if age < 0:
            raise ValueError("received_at is in the future")
        limits = mapping(data.get("rate_limits"), "rate_limits")
        readings = []
        for key, minutes in (("five_hour", 300), ("seven_day", 10080)):
            if limits.get(key) is None:
                continue
            window = mapping(limits[key], key)
            used = percentage(window.get("used_percentage"), f"{key}.used_percentage")
            reset = window.get("resets_at")
            resets_at = epoch_time(reset, f"{key}.resets_at") if reset is not None else None
            readings.append(Reading(used, minutes, resets_at))
        if not readings:
            raise ValueError("rate_limits has no five_hour or seven_day window")
        return max(readings, key=lambda reading: reading.used_percent)
    except (OSError, ValueError, OverflowError) as error:
        return Unavailable(f"Claude usage {path}: {type(error).__name__}: {error}")
