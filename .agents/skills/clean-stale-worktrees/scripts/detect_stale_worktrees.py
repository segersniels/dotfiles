#!/usr/bin/env python3
"""Detect stale linked Git worktrees and emit a JSON manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Iterable

SCHEMA_VERSION = 1


class InspectionError(RuntimeError):
    pass


def decode(value: bytes) -> str:
    return value.decode("utf-8", "surrogateescape")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        ["git", "-C", os.fspath(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        check=False,
    )


def checked_git(repo: Path, *args: str) -> bytes:
    result = git(repo, *args)
    if result.returncode != 0:
        detail = decode(result.stderr).strip() or "no error detail"
        raise InspectionError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return result.stdout


def repository_root(repo: Path) -> Path:
    result = git(repo, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        detail = decode(result.stderr).strip() or "not a Git worktree"
        raise InspectionError(f"--repo is not inside a Git worktree: {repo}. {detail}")
    return Path(decode(result.stdout).strip()).resolve(strict=True)


def parse_worktrees(repo: Path) -> list[dict[str, Any]]:
    raw = checked_git(repo, "worktree", "list", "--porcelain", "-z")
    records: list[dict[str, Any]] = []
    for encoded_record in raw.split(b"\0\0"):
        if not encoded_record:
            continue
        record: dict[str, Any] = {"locked": False, "prunable": False}
        for encoded_field in encoded_record.split(b"\0"):
            key, separator, value = encoded_field.partition(b" ")
            field = decode(key)
            if field in {"locked", "prunable"}:
                record[field] = True
                if value:
                    record[f"{field}_reason"] = decode(value)
            elif separator:
                record[field.lower()] = decode(value)
            else:
                record[field.lower()] = True
        if "worktree" in record:
            records.append(record)
    if not records:
        raise InspectionError(f"no worktrees found for {repo}")
    return records


def list_active_cwds() -> tuple[list[Path], str | None]:
    if shutil.which("lsof") is None:
        return [], "lsof is not installed"
    result = subprocess.run(
        ["lsof", "-a", "-d", "cwd", "-Fn"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = decode(result.stderr).strip() or "no error detail"
        return [], f"lsof failed with exit {result.returncode}: {detail}"
    paths = [
        Path(decode(line[1:])).resolve(strict=False)
        for line in result.stdout.splitlines()
        if line.startswith(b"n")
    ]
    return paths, None


def contains(root: Path, child: Path) -> bool:
    try:
        return os.path.commonpath((os.fspath(root), os.fspath(child))) == os.fspath(root)
    except ValueError:
        return False


def newest_mtime(roots: Iterable[Path]) -> tuple[float | None, str | None]:
    newest: float | None = None
    errors: list[str] = []

    def inspect(path: Path) -> None:
        nonlocal newest
        try:
            modified = path.lstat().st_mtime
            newest = modified if newest is None else max(newest, modified)
        except OSError as error:
            errors.append(f"{path}: {error.strerror or error}")

    for root in roots:
        inspect(root)
        if not root.is_dir():
            continue

        def onerror(error: OSError) -> None:
            errors.append(f"{error.filename or root}: {error.strerror or error}")

        for directory, dirnames, filenames in os.walk(root, followlinks=False, onerror=onerror):
            base = Path(directory)
            for name in dirnames:
                inspect(base / name)
            for name in filenames:
                inspect(base / name)

    return newest, "; ".join(errors[:5]) if errors else None


def iso_time(timestamp: float | None) -> str | None:
    if timestamp is None:
        return None
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat().replace("+00:00", "Z")


def inspect_worktree(
    raw: dict[str, Any],
    main_path: Path,
    cutoff: float,
    active_cwds: list[Path],
    activity_error: str | None,
) -> dict[str, Any]:
    path = Path(raw["worktree"]).resolve(strict=False)
    result: dict[str, Any] = {
        "path": os.fspath(path),
        "head": raw.get("head"),
        "branch": raw.get("branch", "detached").removeprefix("refs/heads/"),
        "locked": bool(raw.get("locked")),
        "candidate": False,
        "reasons": [],
    }
    reasons: list[str] = result["reasons"]

    if path == main_path:
        reasons.append("main-worktree")
        return result
    if raw.get("prunable") or not path.is_dir():
        reasons.append("missing-or-prunable")
        return result
    if raw.get("locked"):
        reasons.append("locked")

    if activity_error:
        result["active"] = None
        result["activity_error"] = activity_error
        reasons.append("activity-unknown")
    else:
        active = any(contains(path, cwd) for cwd in active_cwds)
        result["active"] = active
        if active:
            reasons.append("active-process-cwd")

    git_dir_result = git(path, "rev-parse", "--path-format=absolute", "--git-dir")
    if git_dir_result.returncode != 0:
        result["inspection_error"] = decode(git_dir_result.stderr).strip()
        reasons.append("gitdir-check-failed")
        return result
    git_dir = Path(decode(git_dir_result.stdout).strip()).resolve(strict=False)
    modified, scan_error = newest_mtime((path, git_dir))
    result["last_modified"] = iso_time(modified)
    result["age_days"] = round((time.time() - modified) / 86400, 2) if modified is not None else None
    if scan_error:
        result["inspection_error"] = scan_error
        reasons.append("filesystem-scan-failed")
    elif modified is None or modified >= cutoff:
        reasons.append("recently-modified")

    status = git(path, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0:
        result["status_error"] = decode(status.stderr).strip()
        reasons.append("status-check-failed")
    else:
        dirty_count = len(status.stdout.splitlines())
        result["dirty_count"] = dirty_count
        if dirty_count:
            reasons.append("dirty")

    head = raw.get("head")
    if not head:
        reasons.append("head-unknown")
    else:
        refs = git(
            path,
            "for-each-ref",
            "--format=%(refname)",
            f"--contains={head}",
            "refs/heads",
            "refs/remotes",
            "refs/tags",
        )
        if refs.returncode != 0:
            result["refs_error"] = decode(refs.stderr).strip()
            reasons.append("refs-check-failed")
        else:
            preserving_refs = [decode(line) for line in refs.stdout.splitlines() if line]
            result["preserving_refs"] = preserving_refs
            if not preserving_refs:
                reasons.append("head-not-preserved")

    if not reasons:
        result["candidate"] = True
        reasons.append("safe-stale-candidate")
    return result


def create_manifest(repo: Path, days: float) -> dict[str, Any]:
    root = repository_root(repo)
    raw_worktrees = parse_worktrees(root)
    main_path = Path(raw_worktrees[0]["worktree"]).resolve(strict=False)
    active_cwds, activity_error = list_active_cwds()
    cutoff = time.time() - days * 86400
    worktrees = [
        inspect_worktree(raw, main_path, cutoff, active_cwds, activity_error)
        for raw in raw_worktrees
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "stale-git-worktrees",
        "generated_at": iso_time(time.time()),
        "repository": os.fspath(root),
        "threshold_days": days,
        "worktrees": worktrees,
        "summary": {
            "total": len(worktrees),
            "candidates": sum(bool(item["candidate"]) for item in worktrees),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect stale linked Git worktrees and emit a JSON manifest.",
        epilog=(
            "Exit codes: 0 success; 2 invalid input, missing prerequisite, or inspection error.\n\n"
            "Examples:\n"
            "  %(prog)s --repo /path/to/repo --days 3\n"
            "  %(prog)s --repo /path/to/repo --days 3 --output /tmp/worktrees.json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path inside the target repository")
    parser.add_argument("--days", type=float, default=3.0, help="Minimum inactivity in days (default: 3)")
    parser.add_argument("--output", type=Path, help="Write JSON to this file instead of stdout")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.days <= 0:
        print(f"Error: --days must be greater than zero; received {args.days}", file=sys.stderr)
        return 2
    if shutil.which("git") is None:
        print("Error: git is not installed", file=sys.stderr)
        return 2
    try:
        manifest = create_manifest(args.repo, args.days)
    except (InspectionError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    serialized = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        try:
            args.output.write_text(serialized, encoding="utf-8")
        except OSError as error:
            print(f"Error: cannot write --output {args.output}: {error}", file=sys.stderr)
            return 2
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
