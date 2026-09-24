"""Write deterministic, path-safe analysis reports."""

from __future__ import annotations

from collections.abc import Iterable
import json
from pathlib import Path
import re
import unicodedata

from .model import CompilerOutput, IRSnapshot, ReportPaths


_MAX_COMPONENT_LENGTH = 48
_UNSAFE_COMPONENT_RE = re.compile(r"[^a-z0-9]+")


def sanitize_component(value: str) -> str:
    """Return a bounded ASCII filename component for untrusted pass metadata."""

    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    component = _UNSAFE_COMPONENT_RE.sub("-", ascii_value).strip("-")
    component = component[:_MAX_COMPONENT_LENGTH].rstrip("-")
    return component or "pass"


def write_report(
    *,
    destination: Path,
    source: Path,
    compiler_output: CompilerOutput,
    captured_count: int,
    snapshots: Iterable[IRSnapshot],
    max_snapshots: int,
    truncated: bool,
) -> ReportPaths:
    """Persist one complete analysis without overwriting a non-empty directory."""

    root = destination.expanduser().resolve()
    if root.exists():
        if not root.is_dir():
            raise ValueError(f"report destination is not a directory: {root}")
        if any(root.iterdir()):
            raise ValueError(f"report destination is not empty: {root}")
    else:
        root.mkdir(parents=True)

    retained = list(snapshots)
    snapshots_dir = root / "snapshots"
    snapshots_dir.mkdir()

    snapshot_entries: list[dict[str, object]] = []
    timeline_entries: list[str] = []
    for index, snapshot in enumerate(retained, start=1):
        filename = f"{index:03d}-{sanitize_component(snapshot.pass_name)}.ll"
        relative_file = (Path("snapshots") / filename).as_posix()
        _write_text(snapshots_dir / filename, snapshot.ir)
        snapshot_entries.append(
            {
                "index": index,
                "pass_name": snapshot.pass_name,
                "scope": snapshot.scope,
                "file": relative_file,
            }
        )
        timeline_entries.extend(
            [
                f"## {index:03d} — {snapshot.pass_name}",
                "",
                f"- Scope: {snapshot.scope}",
                f"- Snapshot: [{filename}]({relative_file})",
                "",
            ]
        )

    manifest_data = {
        "schema_version": 1,
        "source": str(source),
        "clang": str(compiler_output.clang_path),
        "optimization_level": "O1",
        "command": list(compiler_output.command),
        "captured_count": captured_count,
        "retained_count": len(retained),
        "max_snapshots": max_snapshots,
        "truncated": truncated,
        "snapshots": snapshot_entries,
    }

    manifest = root / "manifest.json"
    _write_text(
        manifest,
        json.dumps(manifest_data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )

    timeline = root / "timeline.md"
    timeline_lines = [
        "# LLVM Transformation Timeline",
        "",
        f"Source: {source}",
        f"Compiler: {compiler_output.clang_path}",
        f"Retained transformations: {len(retained)}",
        "",
        *timeline_entries,
    ]
    _write_text(timeline, "\n".join(timeline_lines).rstrip() + "\n")

    return ReportPaths(
        root=root,
        manifest=manifest,
        timeline=timeline,
        snapshots_dir=snapshots_dir,
    )


def _write_text(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
