"""Shared immutable data contracts for the IRis analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IRSnapshot:
    """One ordered LLVM IR state emitted after an optimization pass."""

    order: int
    pass_name: str
    scope: str
    ir: str


@dataclass(frozen=True)
class CompilerOutput:
    """Captured output and provenance for one Clang pipeline invocation."""

    clang_path: Path
    command: tuple[str, ...]
    dump_text: str


@dataclass(frozen=True)
class CLIConfig:
    """Validated inputs for one command-line analysis."""

    source: Path
    clang_override: str | None
    output_dir: Path
    max_snapshots: int


@dataclass(frozen=True)
class ReportPaths:
    """Locations of the report artifacts produced by an analysis."""

    root: Path
    manifest: Path
    timeline: Path
    snapshots_dir: Path
