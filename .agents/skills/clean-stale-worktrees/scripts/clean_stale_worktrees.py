#!/usr/bin/env python3
"""Revalidate and remove candidates from a stale-worktree manifest."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Optional

from detect_stale_worktrees import (
    SCHEMA_VERSION,
    InspectionError,
    decode,
    git,
    inspect_worktree,
    list_active_cwds,
    parse_worktrees,
    repository_root,
)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise InspectionError(f"cannot read manifest {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise InspectionError(f"manifest is not valid JSON: {error}") from error

    if not isinstance(manifest, dict):
        raise InspectionError("manifest root must be a JSON object")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise InspectionError(
            f"manifest schema_version must be {SCHEMA_VERSION}; received {manifest.get('schema_version')!r}"
        )
    if manifest.get("kind") != "stale-git-worktrees":
        raise InspectionError("manifest kind must be stale-git-worktrees")
    if not isinstance(manifest.get("repository"), str):
        raise InspectionError("manifest repository must be a path string")
    days = manifest.get("threshold_days")
    if not isinstance(days, (int, float)) or isinstance(days, bool) or days <= 0:
        raise InspectionError("manifest threshold_days must be greater than zero")
    if not isinstance(manifest.get("worktrees"), list):
        raise InspectionError("manifest worktrees must be an array")
    return manifest


def revalidate(repo: Path, candidate_path: Path, days: float) -> Optional[dict[str, Any]]:
    worktrees = parse_worktrees(repo)
    main_path = Path(worktrees[0]["worktree"]).resolve(strict=False)
    raw = next(
        (
            item
            for item in worktrees
            if Path(item["worktree"]).resolve(strict=False) == candidate_path
        ),
        None,
    )
    if raw is None:
        return None
    active_cwds, activity_error = list_active_cwds()
    cutoff = time.time() - days * 86400
    return inspect_worktree(raw, main_path, cutoff, active_cwds, activity_error)


def clean(manifest: dict[str, Any]) -> tuple[dict[str, Any], int]:
    repo = repository_root(Path(manifest["repository"]))
    recorded_repo = Path(manifest["repository"]).resolve(strict=False)
    if repo != recorded_repo:
        raise InspectionError(
            f"manifest repository resolves to {recorded_repo}, but Git reports {repo}"
        )

    days = float(manifest["threshold_days"])
    recorded_candidates = [
        item
        for item in manifest["worktrees"]
        if isinstance(item, dict) and item.get("candidate") is True
    ]
    results: list[dict[str, Any]] = []
    failed = False

    for recorded in recorded_candidates:
        path_value = recorded.get("path")
        head = recorded.get("head")
        if not isinstance(path_value, str) or not isinstance(head, str):
            results.append({"path": path_value, "status": "skipped", "reason": "invalid-candidate-record"})
            continue

        path = Path(path_value).resolve(strict=False)
        current = revalidate(repo, path, days)
        if current is None:
            results.append({"path": os.fspath(path), "status": "skipped", "reason": "no-longer-registered"})
            continue
        if current.get("head") != head:
            results.append(
                {
                    "path": os.fspath(path),
                    "status": "skipped",
                    "reason": "head-changed",
                    "recorded_head": head,
                    "current_head": current.get("head"),
                }
            )
            continue
        if not current.get("candidate"):
            results.append(
                {
                    "path": os.fspath(path),
                    "status": "skipped",
                    "reason": "no-longer-safe",
                    "safety_reasons": current.get("reasons", []),
                }
            )
            continue

        removal = git(repo, "worktree", "remove", os.fspath(path))
        if removal.returncode != 0:
            failed = True
            results.append(
                {
                    "path": os.fspath(path),
                    "status": "failed",
                    "reason": "git-worktree-remove-failed",
                    "error": decode(removal.stderr).strip() or "no error detail",
                }
            )
        elif path.exists():
            failed = True
            results.append(
                {
                    "path": os.fspath(path),
                    "status": "failed",
                    "reason": "directory-still-exists-after-removal",
                }
            )
        else:
            results.append({"path": os.fspath(path), "status": "removed", "directory_removed": True})

    output = {
        "schema_version": SCHEMA_VERSION,
        "kind": "stale-git-worktree-cleanup",
        "repository": os.fspath(repo),
        "threshold_days": days,
        "manifest_candidates": len(recorded_candidates),
        "results": results,
        "summary": {
            "removed": sum(item["status"] == "removed" for item in results),
            "skipped": sum(item["status"] == "skipped" for item in results),
            "failed": sum(item["status"] == "failed" for item in results),
        },
    }
    return output, 3 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Revalidate and remove candidates from a stale-worktree JSON manifest.",
        epilog=(
            "The command removes each registered worktree directory with git worktree remove. "
            "It does not delete branches or use --force.\n\n"
            "Exit codes: 0 success; 2 invalid input, missing prerequisite, or inspection error; "
            "3 one or more removals failed.\n\n"
            "Example:\n"
            "  %(prog)s /tmp/worktrees.json --confirm REMOVE"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("manifest", type=Path, help="Manifest from detect_stale_worktrees.py")
    parser.add_argument("--confirm", metavar="REMOVE", required=True, help="Must be exactly REMOVE")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.confirm != "REMOVE":
        print("Error: --confirm must be exactly REMOVE", file=sys.stderr)
        return 2
    if shutil.which("git") is None:
        print("Error: git is not installed", file=sys.stderr)
        return 2
    try:
        manifest = load_manifest(args.manifest)
        output, exit_code = clean(manifest)
    except (InspectionError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
