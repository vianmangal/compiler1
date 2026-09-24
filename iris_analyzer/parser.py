"""Parse and reduce LLVM pass-manager IR dump output."""

from __future__ import annotations

from collections.abc import Iterable
import re

from .model import IRSnapshot


_AFTER_BANNER_RE = re.compile(
    r"^\s*;?\s*\*{3,}\s*IR Dump After\s+(?P<pass_name>.+?)\s+on\s+"
    r"(?P<scope>.+?)\s*\*{3,}\s*$"
)
_DUMP_BOUNDARY_RE = re.compile(
    r"^\s*;?\s*\*{3,}\s*IR Dump (?:Before|After)\b.*\*{3,}\s*$"
)


def normalize_ir(ir: str) -> str:
    """Return a stable comparison form without changing meaningful IR text."""

    normalized = ir.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip(" \t") for line in normalized.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def parse_ir_dumps(dump_text: str) -> list[IRSnapshot]:
    """Extract changed ``IR Dump After`` sections in stream order.

    The compiler boundary requests LLVM's ``-print-changed`` output. Banners
    explicitly marked ``omitted because no change`` are boundaries, never
    transformations, so only dumps LLVM itself classified as changed become
    snapshots.
    """

    snapshots: list[IRSnapshot] = []
    pass_name: str | None = None
    scope: str | None = None
    body_lines: list[str] = []

    def finish_section() -> None:
        nonlocal pass_name, scope, body_lines
        if pass_name is not None and scope is not None:
            ir = normalize_ir("\n".join(body_lines))
            if ir:
                snapshots.append(
                    IRSnapshot(
                        order=len(snapshots) + 1,
                        pass_name=pass_name,
                        scope=scope,
                        ir=ir,
                    )
                )
        pass_name = None
        scope = None
        body_lines = []

    for line in dump_text.splitlines():
        after_match = _AFTER_BANNER_RE.match(line)
        if after_match:
            finish_section()
            if " omitted because no change" in line:
                continue
            pass_name = after_match.group("pass_name").strip()
            scope = after_match.group("scope").strip()
            continue

        if _DUMP_BOUNDARY_RE.match(line):
            finish_section()
            continue

        if pass_name is not None:
            body_lines.append(line)

    finish_section()
    return snapshots


def retain_changed(
    snapshots: Iterable[IRSnapshot], max_snapshots: int
) -> tuple[list[IRSnapshot], bool]:
    """Cap snapshots that LLVM has already classified as changed.

    The returned boolean is true only when at least one changed snapshot exists
    beyond the requested cap.
    """

    if max_snapshots <= 0:
        raise ValueError("max_snapshots must be positive")

    retained: list[IRSnapshot] = []
    for snapshot in snapshots:
        if len(retained) == max_snapshots:
            return retained, True
        retained.append(snapshot)
    return retained, False
