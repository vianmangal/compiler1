"""Safe discovery and invocation of the local Clang optimization pipeline."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import BinaryIO

from .model import CompilerOutput


_PIPELINE_TIMEOUT_SECONDS = 30
_MAX_DIAGNOSTIC_CHARS = 4_000
_MAX_DUMP_BYTES = 16 * 1024 * 1024
_POLL_INTERVAL_SECONDS = 0.01


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
        "-mllvm",
        "-print-module-scope",
        str(resolved_source),
        "-o",
        os.devnull,
    )

    try:
        with tempfile.TemporaryFile() as dump_stream:
            process = subprocess.Popen(
                command,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=dump_stream,
            )
            deadline = time.monotonic() + _PIPELINE_TIMEOUT_SECONDS
            while process.poll() is None:
                if _stream_size(dump_stream) > _MAX_DUMP_BYTES:
                    _stop_process(process)
                    raise CompilerError(
                        "Clang pass output exceeded the 16 MiB safety limit"
                    )
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    _stop_process(process)
                    raise CompilerError(
                        f"Clang optimization pipeline timed out after "
                        f"{_PIPELINE_TIMEOUT_SECONDS} seconds"
                    )
                time.sleep(min(_POLL_INTERVAL_SECONDS, remaining))

            if _stream_size(dump_stream) > _MAX_DUMP_BYTES:
                raise CompilerError(
                    "Clang pass output exceeded the 16 MiB safety limit"
                )
            dump_stream.seek(0)
            dump_text = dump_stream.read(_MAX_DUMP_BYTES + 1).decode(
                "utf-8", errors="replace"
            )
            returncode = process.returncode
    except OSError as exc:
        raise CompilerError(f"Could not run Clang: {exc}") from exc

    if returncode != 0:
        diagnostic = _bounded_diagnostic(dump_text)
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
            f"Clang failed with exit code {returncode}: {diagnostic}"
        )

    return CompilerOutput(
        clang_path=resolved_clang,
        command=command,
        dump_text=dump_text,
    )


def _stream_size(stream: BinaryIO) -> int:
    stream.seek(0, os.SEEK_END)
    return stream.tell()


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    """Terminate a compiler that crossed a resource boundary."""

    process.terminate()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def _bounded_diagnostic(stderr: str | None) -> str:
    diagnostic = (stderr or "").strip()
    if not diagnostic:
        return "no diagnostic output"
    if len(diagnostic) <= _MAX_DIAGNOSTIC_CHARS:
        return diagnostic
    return diagnostic[:_MAX_DIAGNOSTIC_CHARS] + "... [truncated]"
