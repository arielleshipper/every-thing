#!/usr/bin/env python3
"""Validate and atomically record one hed/dek decision lineage revision."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HISTORY = SKILL_ROOT / "references" / "selection-history.jsonl"
CHOOSERS = {"user", "editor", "team", "unknown"}
BASES = {"choice", "edit", "explicit"}
KINDS = {"style", "accuracy", "format"}


def nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def optional_string(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value.strip()


def string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return [item.strip() for item in value if item.strip()]


def validate_learning_evidence(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("learning_evidence must be a list")
    validated = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"learning_evidence[{index}] must be an object")
        allowed = {"preference_id", "signal", "scope", "basis", "kind"}
        extras = sorted(set(item) - allowed)
        if extras:
            raise ValueError(
                f"learning_evidence[{index}] has unexpected fields: {', '.join(extras)}"
            )
        evidence = {
            "preference_id": nonempty_string(
                item.get("preference_id"), f"learning_evidence[{index}].preference_id"
            ),
            "signal": nonempty_string(item.get("signal"), f"learning_evidence[{index}].signal"),
            "scope": nonempty_string(item.get("scope"), f"learning_evidence[{index}].scope"),
            "basis": nonempty_string(item.get("basis"), f"learning_evidence[{index}].basis"),
            "kind": nonempty_string(item.get("kind"), f"learning_evidence[{index}].kind"),
        }
        if evidence["basis"] not in BASES:
            raise ValueError(f"learning_evidence[{index}].basis must be one of {sorted(BASES)}")
        if evidence["kind"] not in KINDS:
            raise ValueError(f"learning_evidence[{index}].kind must be one of {sorted(KINDS)}")
        validated.append(evidence)
    return validated


def validate_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    allowed = {
        "decision_id",
        "article_identifier",
        "format",
        "thesis",
        "chooser",
        "chosen_hed",
        "chosen_dek",
        "source_option",
        "material_edits",
        "user_reason",
        "observable_contrasts",
        "learning_evidence",
    }
    extras = sorted(set(payload) - allowed)
    if extras:
        raise ValueError(f"unexpected payload fields: {', '.join(extras)}")

    chooser = nonempty_string(payload.get("chooser"), "chooser")
    if chooser not in CHOOSERS:
        raise ValueError(f"chooser must be one of {sorted(CHOOSERS)}")

    return {
        "decision_id": nonempty_string(payload.get("decision_id"), "decision_id"),
        "article_identifier": nonempty_string(
            payload.get("article_identifier"), "article_identifier"
        ),
        "format": nonempty_string(payload.get("format"), "format"),
        "thesis": nonempty_string(payload.get("thesis"), "thesis"),
        "chooser": chooser,
        "chosen_hed": nonempty_string(payload.get("chosen_hed"), "chosen_hed"),
        "chosen_dek": nonempty_string(payload.get("chosen_dek"), "chosen_dek"),
        "source_option": optional_string(payload.get("source_option"), "source_option"),
        "material_edits": optional_string(payload.get("material_edits"), "material_edits"),
        "user_reason": optional_string(payload.get("user_reason"), "user_reason"),
        "observable_contrasts": string_list(
            payload.get("observable_contrasts"), "observable_contrasts"
        ),
        "learning_evidence": validate_learning_evidence(payload.get("learning_evidence")),
    }


def validate_revision(revision: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(revision, dict):
        raise ValueError(f"history line {line_number}: revision must be an object")
    required = {
        "revision",
        "recorded_at",
        "chosen_hed",
        "chosen_dek",
        "source_option",
        "material_edits",
        "user_reason",
        "observable_contrasts",
        "learning_evidence",
    }
    if set(revision) != required:
        raise ValueError(f"history line {line_number}: revision fields are invalid")
    if not isinstance(revision["revision"], int) or revision["revision"] < 1:
        raise ValueError(f"history line {line_number}: revision number is invalid")
    nonempty_string(revision["recorded_at"], "recorded_at")
    nonempty_string(revision["chosen_hed"], "chosen_hed")
    nonempty_string(revision["chosen_dek"], "chosen_dek")
    optional_string(revision["source_option"], "source_option")
    optional_string(revision["material_edits"], "material_edits")
    optional_string(revision["user_reason"], "user_reason")
    string_list(revision["observable_contrasts"], "observable_contrasts")
    validate_learning_evidence(revision["learning_evidence"])
    return revision


def validate_history_record(record: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(f"history line {line_number}: record must be an object")
    required = {
        "decision_id",
        "article_identifier",
        "format",
        "thesis",
        "chooser",
        "revisions",
    }
    if set(record) != required:
        raise ValueError(f"history line {line_number}: record fields are invalid")
    for field in ("decision_id", "article_identifier", "format", "thesis"):
        nonempty_string(record[field], field)
    if record["chooser"] not in CHOOSERS:
        raise ValueError(f"history line {line_number}: chooser is invalid")
    if not isinstance(record["revisions"], list) or not record["revisions"]:
        raise ValueError(f"history line {line_number}: revisions must be non-empty")
    for revision in record["revisions"]:
        validate_revision(revision, line_number)
    expected = list(range(1, len(record["revisions"]) + 1))
    actual = [revision["revision"] for revision in record["revisions"]]
    if actual != expected:
        raise ValueError(f"history line {line_number}: revisions must be sequential")
    return record


def read_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = validate_history_record(json.loads(line), line_number)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at history line {line_number}: {exc}") from exc
        if record["decision_id"] in seen:
            raise ValueError(f"duplicate decision_id: {record['decision_id']}")
        seen.add(record["decision_id"])
        records.append(record)
    return records


def atomic_write(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temporary_path = Path(handle.name)
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary_path, path)


def article_identity(record: dict[str, Any]) -> tuple[str, str]:
    return (
        " ".join(record["format"].casefold().split()),
        " ".join(record["article_identifier"].casefold().split()),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--record-file", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    try:
        records = read_history(args.history)
        if args.validate_only:
            print(f"valid: {len(records)} decision lineage(s)")
            return 0
        if args.record_file is None:
            raise ValueError("--record-file is required unless --validate-only is used")

        payload = validate_payload(json.loads(args.record_file.read_text()))
        index = next(
            (
                i
                for i, record in enumerate(records)
                if record["decision_id"] == payload["decision_id"]
            ),
            None,
        )
        revision = {
            "revision": 1 if index is None else len(records[index]["revisions"]) + 1,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "chosen_hed": payload["chosen_hed"],
            "chosen_dek": payload["chosen_dek"],
            "source_option": payload["source_option"],
            "material_edits": payload["material_edits"],
            "user_reason": payload["user_reason"],
            "observable_contrasts": payload["observable_contrasts"],
            "learning_evidence": payload["learning_evidence"],
        }

        if index is None:
            incoming_identity = article_identity(payload)
            duplicate = next(
                (
                    record
                    for record in records
                    if article_identity(record) == incoming_identity
                ),
                None,
            )
            if duplicate is not None:
                raise ValueError(
                    "this article already exists under decision_id "
                    f"{duplicate['decision_id']}; reuse that ID for revisions"
                )
            records.append(
                {
                    "decision_id": payload["decision_id"],
                    "article_identifier": payload["article_identifier"],
                    "format": payload["format"],
                    "thesis": payload["thesis"],
                    "chooser": payload["chooser"],
                    "revisions": [revision],
                }
            )
            action = "recorded"
        else:
            record = records[index]
            record["article_identifier"] = payload["article_identifier"]
            record["format"] = payload["format"]
            record["thesis"] = payload["thesis"]
            if payload["chooser"] != "unknown" or record["chooser"] == "unknown":
                record["chooser"] = payload["chooser"]
            record["revisions"].append(revision)
            action = "revised"

        atomic_write(args.history, records)
        print(
            f"{action} {payload['decision_id']} revision {revision['revision']}; "
            f"history contains {len(records)} decision lineage(s)"
        )
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
