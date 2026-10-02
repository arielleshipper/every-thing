#!/usr/bin/env python3
"""Validate decision history and learned preference activation thresholds."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from record_selection import DEFAULT_HISTORY, article_identity, read_history


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFERENCES = SKILL_ROOT / "references" / "learned-preferences.json"
BUCKETS = ("active", "provisional", "retired")
BASES = {"explicit", "inferred", "mixed"}


def validate_preference(item: Any, bucket: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(f"{bucket} preference must be an object")
    required = {
        "id",
        "signal",
        "scope",
        "basis",
        "evidence_decision_ids",
        "counterevidence_decision_ids",
        "last_updated",
    }
    if set(item) != required:
        raise ValueError(f"preference in {bucket} has invalid fields")
    for field in ("id", "signal", "scope", "basis", "last_updated"):
        if not isinstance(item[field], str) or not item[field].strip():
            raise ValueError(f"preference {field} must be a non-empty string")
    if item["basis"] not in BASES:
        raise ValueError(f"preference basis must be one of {sorted(BASES)}")
    for field in ("evidence_decision_ids", "counterevidence_decision_ids"):
        value = item[field]
        if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value):
            raise ValueError(f"preference {field} must be a list of non-empty strings")
        if len(value) != len(set(value)):
            raise ValueError(f"preference {field} contains duplicates")
    if set(item["evidence_decision_ids"]) & set(item["counterevidence_decision_ids"]):
        raise ValueError("the same decision cannot be evidence and counterevidence")
    return item


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--preferences", type=Path, default=DEFAULT_PREFERENCES)
    args = parser.parse_args()

    try:
        history = read_history(args.history)
        history_by_id = {record["decision_id"]: record for record in history}
        preferences = json.loads(args.preferences.read_text())
        if not isinstance(preferences, dict) or set(preferences) != {"version", *BUCKETS}:
            raise ValueError("preference store must contain version, active, provisional, and retired")
        if preferences["version"] != 1:
            raise ValueError("unsupported preference store version")

        seen_preference_ids: set[str] = set()
        count = 0
        for bucket in BUCKETS:
            if not isinstance(preferences[bucket], list):
                raise ValueError(f"{bucket} must be a list")
            for raw_item in preferences[bucket]:
                item = validate_preference(raw_item, bucket)
                count += 1
                if item["id"] in seen_preference_ids:
                    raise ValueError(f"duplicate preference id: {item['id']}")
                seen_preference_ids.add(item["id"])

                referenced = item["evidence_decision_ids"] + item["counterevidence_decision_ids"]
                missing = sorted(set(referenced) - set(history_by_id))
                if missing:
                    raise ValueError(
                        f"preference {item['id']} references unknown decisions: {', '.join(missing)}"
                    )

                matching_evidence = []
                for decision_id in item["evidence_decision_ids"]:
                    latest_revision = history_by_id[decision_id]["revisions"][-1]
                    if any(
                        evidence["preference_id"] == item["id"]
                        for evidence in latest_revision["learning_evidence"]
                    ):
                        matching_evidence.append(decision_id)
                if set(matching_evidence) != set(item["evidence_decision_ids"]):
                    raise ValueError(
                        f"preference {item['id']} lacks matching history evidence for every decision"
                    )

                if bucket == "active":
                    explicit = any(
                        evidence["preference_id"] == item["id"] and evidence["basis"] == "explicit"
                        for decision_id in item["evidence_decision_ids"]
                        for evidence in history_by_id[decision_id]["revisions"][-1]["learning_evidence"]
                    )
                    if item["basis"] == "inferred":
                        identities = {
                            article_identity(history_by_id[decision_id])
                            for decision_id in item["evidence_decision_ids"]
                        }
                        if len(identities) < 3:
                            raise ValueError(
                                f"active inferred preference {item['id']} needs three distinct articles"
                            )
                    if item["basis"] in {"explicit", "mixed"} and not explicit:
                        raise ValueError(
                            f"active {item['basis']} preference {item['id']} needs explicit evidence"
                        )

        print(
            f"valid: {len(history)} decision lineage(s), {count} learned preference(s)"
        )
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
