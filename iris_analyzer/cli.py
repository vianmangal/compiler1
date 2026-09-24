"""Command-line interface for the IRis transformation analyzer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from .compiler import CompilerError, resolve_clang, run_optimization_pipeline
from .model import CLIConfig
from .parser import parse_ir_dumps, retain_changed
from .reporting import write_report


class CLIError(ValueError):
    """A concise user-facing command or input error."""


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CLIError(message)


def _positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    """Build the Phase 1 command parser."""

    parser = _ArgumentParser(
        prog="python -m iris_analyzer",
        description="Show which LLVM optimization passes changed a C program's IR.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    analyze = subcommands.add_parser(
        "analyze",
        help="analyze one local C source file",
    )
    analyze.add_argument("source", metavar="SOURCE", type=Path)
    analyze.add_argument(
        "--clang",
        metavar="EXECUTABLE",
        help="Clang executable path or command name (default: clang from PATH)",
    )
    analyze.add_argument(
        "--output",
        metavar="DIRECTORY",
        type=Path,
        help="report directory (default: ./SOURCE_STEM-iris-report)",
    )
    analyze.add_argument(
        "--max-snapshots",
        metavar="N",
        type=_positive_integer,
        default=50,
        help="maximum retained transformations (default: 50)",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse exactly one supported Phase 1 command."""

    return build_parser().parse_args(argv)


def validate_source(path: Path) -> Path:
    """Validate and resolve one existing lower-case ``.c`` source file."""

    candidate = path.expanduser()
    if not candidate.exists():
        raise CLIError(f"source file does not exist: {candidate}")
    if not candidate.is_file():
        raise CLIError(f"source path is not a regular file: {candidate}")
    if candidate.suffix != ".c":
        raise CLIError(f"source file must use the lower-case .c extension: {candidate}")
    return candidate.resolve()


def main(argv: Sequence[str] | None = None) -> int:
    """Run one analysis and return a process-style exit code."""

    try:
        args = parse_args(argv)
        source = validate_source(args.source)
        output_dir = (
            args.output.expanduser()
            if args.output is not None
            else Path.cwd() / f"{source.stem}-iris-report"
        )
        config = CLIConfig(
            source=source,
            clang_override=args.clang,
            output_dir=output_dir,
            max_snapshots=args.max_snapshots,
        )

        clang_path = resolve_clang(config.clang_override)
        compiler_output = run_optimization_pipeline(config.source, clang_path)
        captured = parse_ir_dumps(compiler_output.dump_text)
        if not captured:
            raise CLIError("no LLVM IR snapshots found in Clang output")
        retained, truncated = retain_changed(captured, config.max_snapshots)
        report = write_report(
            destination=config.output_dir,
            source=config.source,
            compiler_output=compiler_output,
            captured_count=len(captured),
            snapshots=retained,
            max_snapshots=config.max_snapshots,
            truncated=truncated,
        )
    except (CLIError, CompilerError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except SystemExit as exc:
        return int(exc.code or 0)

    noun = "transformation" if len(retained) == 1 else "transformations"
    print(f"Retained {len(retained)} {noun}. Report: {report.root}")
    return 0
