#!/usr/bin/env python3
"""Validate the recorded decisions in a check-protection audit."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from enum import Enum
from pathlib import Path


class Choice(Enum):
    """The audit's available actions, checked before its plan is used."""

    RUN = "run"
    NARROW = "narrow"
    REUSE = "reuse"
    OMIT = "omit"
    WAIT = "wait"


class DecisionRecordError(ValueError):
    """The audit cannot proceed while a decision record is incomplete."""


class HeaderMismatch(DecisionRecordError):
    """The file does not identify the six audit fields."""


class ColumnCountMismatch(DecisionRecordError):
    """A row cannot be interpreted as one complete decision."""


class MissingField(DecisionRecordError):
    """A proposed check lacks part of its recorded justification."""


class InvalidChoice(DecisionRecordError):
    """An audit row names an action outside the supported choices."""


class DuplicateCommand(DecisionRecordError):
    """The same command has more than one recorded decision."""


class EmptyInventory(DecisionRecordError):
    """There are no proposed checks to audit."""


HEADER = ("command", "protection", "cheaper", "decision", "reason", "evidence")


def read_decisions(path: Path) -> tuple[Choice, ...]:
    """Read complete audit rows, rejecting missing or contradictory records."""

    with path.open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream, delimiter="\t", strict=True)
        header = tuple(next(rows, ()))
        if header != HEADER:
            raise HeaderMismatch(f"Header {header!r} must be {HEADER!r}.")
        decisions: list[Choice] = []
        commands: set[str] = set()
        for row in rows:
            if len(row) != len(HEADER):
                raise ColumnCountMismatch(
                    f"Line {rows.line_num}: found {len(row)} fields; expected {len(HEADER)}."
                )
            fields = tuple(field.strip() for field in row)
            if not all(fields):
                missing = tuple(name for name, value in zip(HEADER, fields) if not value)
                raise MissingField(f"Line {rows.line_num}: missing fields {missing!r}.")
            command, _protection, _cheaper, choice_text, _reason, _evidence = fields
            try:
                choice = Choice(choice_text)
            except ValueError as error:
                raise InvalidChoice(
                    f"Line {rows.line_num}: {choice_text!r} must be run, narrow, reuse, omit or wait."
                ) from error
            if command in commands:
                raise DuplicateCommand(f"Line {rows.line_num}: decide once for {command!r}.")
            commands.add(command)
            decisions.append(choice)
        if not decisions:
            raise EmptyInventory("Inventory every proposed check; the audit has no decisions.")
        return tuple(decisions)


def main() -> int:
    """Report incomplete audit decisions with a failing process exit status."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    arguments = parser.parse_args()
    try:
        decisions = read_decisions(arguments.record)
    except (OSError, UnicodeError, csv.Error, DecisionRecordError) as error:
        logging.error("Check decisions incomplete: %s", error)
        return 1
    logging.info(
        "Recorded decisions for %s checks. Review their claimed protection before acting.", len(decisions)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
