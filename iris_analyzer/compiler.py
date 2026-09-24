"""Safe discovery and invocation of the local Clang optimization pipeline."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

from .model import CompilerOutput


_PIPELINE_TIMEOUT_SECONDS = 30
_MAX_DIAGNOSTIC_CHARS = 4_000


class CompilerError(RuntimeError):
    """A bounded, user-facing failure at the local compiler boundary."""


def resolve_clang(override: str | None) -> Path:
    """Resolve the default or explicitly selected Clang executable."""

    requested = os.path.expanduser(override) if override else "clang"
    discovered = shutil.which(requested)
    if discovered is None:
        raise CompilerError(f"Clang executable not found: {override or 'clang'}")

    resolved = Path(discovered).resolve()
    if not resolved.is_file():
        raise CompilerError(f"Clang candidate is not a regular file: {resolved}")
    if not os.access(resolved, os.X_OK):
        raise CompilerError(f"Clang candidate is not executable: {resolved}")
    return resolved


def run_optimization_pipeline(source: Path, clang_path: Path) -> CompilerOutput:
    """Run Clang's O1 pipeline with changed-pass instrumentation enabled."""

    resolved_clang = clang_path.expanduser().resolve()
    resolved_source = source.expanduser().resolve()
    command = (
        str(resolved_clang),
        "-O1",
        "-S",
        "-emit-llvm",
        "-mllvm",
        "-print-changed",
        str(resolved_source),
        "-o",
        os.devnull,
    )

    try:
        completed = subprocess.run(
            command,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=_PIPELINE_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CompilerError(
            f"Clang optimization pipeline timed out after "
            f"{_PIPELINE_TIMEOUT_SECONDS} seconds"
        ) from exc
    except OSError as exc:
        raise CompilerError(f"Could not run Clang: {exc}") from exc

    if completed.returncode != 0:
        diagnostic = _bounded_diagnostic(completed.stderr)
        if "print-changed" in diagnostic and (
            "Unknown command line argument" in diagnostic
            or "unknown argument" in diagnostic.lower()
        ):
            raise CompilerError(
                "This Clang does not support the required LLVM "
                "-print-changed instrumentation; select a compatible Clang "
                "with --clang"
            )
        raise CompilerError(
            f"Clang failed with exit code {completed.returncode}: {diagnostic}"
        )

    return CompilerOutput(
        clang_path=resolved_clang,
        command=command,
        dump_text=completed.stderr,
    )


def _bounded_diagnostic(stderr: str | None) -> str:
    diagnostic = (stderr or "").strip()
    if not diagnostic:
        return "no diagnostic output"
    if len(diagnostic) <= _MAX_DIAGNOSTIC_CHARS:
        return diagnostic
    return diagnostic[:_MAX_DIAGNOSTIC_CHARS] + "... [truncated]"
