from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOTS = (
    "architecture",
    "candidates",
    "docs",
    "experiments",
    "portfolio",
    "research",
    "schemas",
)
ROOT_EVIDENCE_FILES = ("README.md",)
GIT_OID = re.compile(r"^[0-9a-f]{40}$")
CURRENTNESS_BASELINE_PATH = "portfolio/PUBLIC_CURRENTNESS_BASELINE_20260924_V2.json"


class ImpactTraceError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ImpactTraceError(f"{path} must contain a JSON object")
    return payload


def _iter_evidence_files(root: Path):
    for relative in ROOT_EVIDENCE_FILES:
        path = root / relative
        if path.is_file():
            yield path
    for relative in EVIDENCE_ROOTS:
        base = root / relative
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                yield path


def _line_hits(path: Path, needle: str) -> list[int]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return [
        index
        for index, line in enumerate(text.splitlines(), start=1)
        if needle in line
    ]


def _subject_head(subject: Any, *, label: str) -> str:
    if not isinstance(subject, dict):
        raise ImpactTraceError(f"{label} must be an object")
    head = subject.get("head")
    if not isinstance(head, str) or not GIT_OID.fullmatch(head):
        raise ImpactTraceError(f"{label} head must be a lowercase 40-hex Git object id")
    return head


def _subject_name(subject: Any, *, label: str) -> str:
    if not isinstance(subject, dict):
        raise ImpactTraceError(f"{label} must be an object")
    name = subject.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ImpactTraceError(f"{label} name must be a non-empty string")
    return name.strip()


def trace_exact_head_references(
    report: dict[str, Any],
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    if report.get("schema") != "DISCOVERY_PUBLIC_CURRENTNESS_REPORT_V1":
        raise ImpactTraceError("unexpected public currentness report schema")

    status = report.get("status")
    if status not in {"CURRENT", "STALE"}:
        raise ImpactTraceError("public currentness status must be CURRENT or STALE")

    evidence_files = tuple(_iter_evidence_files(root))
    subjects: list[dict[str, Any]] = []

    for moved in report.get("moved", []):
        if not isinstance(moved, dict):
            raise ImpactTraceError("moved currentness entry must be an object")
        expected = moved.get("expected_subject")
        observed = moved.get("observed_subject")
        name = _subject_name(expected, label="moved expected_subject")
        head = _subject_head(expected, label=f"{name} expected_subject")
        observed_head = _subject_head(observed, label=f"{name} observed_subject")
        change_fields = sorted(
            str(field)
            for field in (
                moved.get("changes", {}).keys()
                if isinstance(moved.get("changes"), dict)
                else ()
            )
        )
        references = []
        for path in evidence_files:
            hits = _line_hits(path, head)
            if hits:
                references.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "lines": hits,
                        "occurrence_count": len(hits),
                    }
                )
        blocking_references = [
            reference
            for reference in references
            if reference["path"] != CURRENTNESS_BASELINE_PATH
        ]
        subjects.append(
            {
                "name": name,
                "change_kind": "MOVED",
                "change_fields": change_fields,
                "expected_head": head,
                "observed_head": observed_head,
                "exact_old_head_references": references,
                "blocking_exact_old_head_references": blocking_references,
                "reference_state": (
                    "EXACT_REFERENCES_FOUND"
                    if references
                    else "NO_EXACT_REFERENCE_FOUND"
                ),
                "impact_gate": (
                    "BLOCK"
                    if (
                        set(change_fields) - {"head", "tree_sha"}
                        or blocking_references
                    )
                    else "OBSERVE_ONLY"
                ),
            }
        )

    for removed in report.get("removed_subjects", []):
        name = _subject_name(removed, label="removed_subject")
        head = _subject_head(removed, label=f"{name} removed_subject")
        references = []
        for path in evidence_files:
            hits = _line_hits(path, head)
            if hits:
                references.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "lines": hits,
                        "occurrence_count": len(hits),
                    }
                )
        subjects.append(
            {
                "name": name,
                "change_kind": "REMOVED",
                "change_fields": ["repository_membership"],
                "expected_head": head,
                "observed_head": None,
                "exact_old_head_references": references,
                "blocking_exact_old_head_references": references,
                "reference_state": (
                    "EXACT_REFERENCES_FOUND"
                    if references
                    else "NO_EXACT_REFERENCE_FOUND"
                ),
                "impact_gate": "BLOCK",
            }
        )

    new_subjects = []
    for added in report.get("added_subjects", []):
        name = _subject_name(added, label="added_subject")
        head = _subject_head(added, label=f"{name} added_subject")
        new_subjects.append(
            {
                "name": name,
                "observed_head": head,
                "disposition": "UNCLASSIFIED_NEW_PUBLIC_SUBJECT",
            }
        )

    referenced = sum(
        1 for item in subjects if item["reference_state"] == "EXACT_REFERENCES_FOUND"
    )
    unresolved = sum(
        1 for item in subjects if item["reference_state"] == "NO_EXACT_REFERENCE_FOUND"
    )
    blocking_subjects = [
        item for item in subjects if item.get("impact_gate") == "BLOCK"
    ]
    if status == "CURRENT":
        gate_status = "CURRENT"
    elif new_subjects or blocking_subjects:
        gate_status = "BLOCKING_CURRENTNESS_IMPACT"
    else:
        gate_status = "NONBLOCKING_EXACT_HEAD_DRIFT"

    return {
        "schema": "DISCOVERY_PUBLIC_IMPACT_REPORT_V1",
        "status": (
            "NO_STALE_PUBLIC_SUBJECTS"
            if status == "CURRENT"
            else "STALE_PUBLIC_SUBJECTS_TRACED"
        ),
        "source_currentness_status": status,
        "source_invalidation_reasons": report.get("invalidation_reasons", []),
        "stale_subject_count": len(subjects),
        "subjects_with_exact_references": referenced,
        "subjects_without_exact_references": unresolved,
        "blocking_subject_count": len(blocking_subjects),
        "gate_status": gate_status,
        "subjects": subjects,
        "new_subjects": new_subjects,
        "negative_evidence_rule": (
            "NO_EXACT_REFERENCE_FOUND does not prove that no dependency exists; "
            "it only proves that this exact old head string was not found in the "
            "bounded Discovery evidence surface. The impact gate therefore speaks "
            "only to exact-head-bound Discovery evidence, not semantic dependency."
        ),
        "impact_gate_rule": (
            "Repository additions/removals, default-branch/archive changes, or exact "
            "old-head references outside the currentness baseline are blocking. "
            "Head/tree-only drift whose old head is referenced only by the baseline "
            "is reported as stale but does not fail the bounded exact-reference gate."
        ),
        "claim_ceiling": (
            "EXACT_STALE_HEAD_TEXT_REFERENCE_GATE_ONLY_"
            "NO_SEMANTIC_DEPENDENCY_NO_AUTOMATIC_REPAIR"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Trace stale public exact-head references through Discovery evidence."
        )
    )
    parser.add_argument("currentness_report", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        result = trace_exact_head_references(
            _load(args.currentness_report),
            root=args.root.resolve(),
        )
    except ImpactTraceError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
