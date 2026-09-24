from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iris_analyzer.cli import CLIError, main, parse_args, validate_source
from iris_analyzer.compiler import CompilerError
from iris_analyzer.model import CompilerOutput


PASS_DUMP = """\
*** IR Dump After ChangePass on sum ***
define i32 @sum() {
  ret i32 1
}
*** IR Dump After NoOpPass on sum omitted because no change ***
*** IR Dump After FinalPass on sum ***
define i32 @sum() {
  ret i32 2
}
"""


class ParseArgsTests(unittest.TestCase):
    def test_accepts_exact_command_and_defaults(self) -> None:
        args = parse_args(["analyze", "program.c"])

        self.assertEqual(args.command, "analyze")
        self.assertEqual(args.source, Path("program.c"))
        self.assertIsNone(args.clang)
        self.assertIsNone(args.output)
        self.assertEqual(args.max_snapshots, 50)

    def test_accepts_all_documented_overrides(self) -> None:
        args = parse_args(
            [
                "analyze",
                "program.c",
                "--clang",
                "custom-clang",
                "--output",
                "report",
                "--max-snapshots",
                "7",
            ]
        )

        self.assertEqual(args.clang, "custom-clang")
        self.assertEqual(args.output, Path("report"))
        self.assertEqual(args.max_snapshots, 7)

    def test_rejects_non_positive_cap_and_extra_source(self) -> None:
        for argv in (
            ["analyze", "program.c", "--max-snapshots", "0"],
            ["analyze", "program.c", "--max-snapshots", "-1"],
            ["analyze", "one.c", "two.c"],
        ):
            with self.subTest(argv=argv):
                with self.assertRaises(CLIError):
                    parse_args(argv)


class ValidateSourceTests(unittest.TestCase):
    def test_accepts_one_existing_lower_case_c_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "program.c"
            source.write_text("int main(void) { return 0; }\n", encoding="utf-8")

            self.assertEqual(validate_source(source), source.resolve())

    def test_rejects_missing_directory_and_wrong_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            upper = root / "program.C"
            upper.write_text("int x;\n", encoding="utf-8")
            for candidate, message in (
                (root / "missing.c", "does not exist"),
                (root, "regular file"),
                (upper, "lower-case .c"),
            ):
                with self.subTest(candidate=candidate):
                    with self.assertRaisesRegex(CLIError, message):
                        validate_source(candidate)


class MainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "program.c"
        self.source.write_text("int main(void) { return 0; }\n", encoding="utf-8")
        self.clang = self.root / "clang"
        self.clang.write_text("fake executable\n", encoding="utf-8")
        self.output = self.root / "report"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def invoke(self, *extra: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = ["analyze", str(self.source), "--output", str(self.output), *extra]
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def successful_capture(self) -> CompilerOutput:
        return CompilerOutput(
            clang_path=self.clang.resolve(),
            command=(str(self.clang.resolve()), "-O1", str(self.source.resolve())),
            dump_text=PASS_DUMP,
        )

    def test_success_wires_capture_filter_cap_and_report_once(self) -> None:
        capture = self.successful_capture()
        with (
            patch("iris_analyzer.cli.resolve_clang", return_value=self.clang.resolve()) as resolve,
            patch("iris_analyzer.cli.run_optimization_pipeline", return_value=capture) as run,
        ):
            code, stdout, stderr = self.invoke("--max-snapshots", "1")

        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("Retained 1 transformation", stdout)
        self.assertIn(str(self.output.resolve()), stdout)
        resolve.assert_called_once_with(None)
        run.assert_called_once_with(self.source.resolve(), self.clang.resolve())

        manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["captured_count"], 2)
        self.assertEqual(manifest["retained_count"], 1)
        self.assertEqual(manifest["max_snapshots"], 1)
        self.assertTrue(manifest["truncated"])
        self.assertEqual(len(list((self.output / "snapshots").glob("*.ll"))), 1)

    def test_uses_explicit_clang_override(self) -> None:
        capture = self.successful_capture()
        with (
            patch("iris_analyzer.cli.resolve_clang", return_value=self.clang.resolve()) as resolve,
            patch("iris_analyzer.cli.run_optimization_pipeline", return_value=capture),
        ):
            code, _, _ = self.invoke("--clang", "chosen-clang")

        self.assertEqual(code, 0)
        resolve.assert_called_once_with("chosen-clang")

    def test_default_output_uses_source_stem_in_current_directory(self) -> None:
        capture = self.successful_capture()
        expected = self.root / "program-iris-report"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch("iris_analyzer.cli.Path.cwd", return_value=self.root),
            patch("iris_analyzer.cli.resolve_clang", return_value=self.clang.resolve()),
            patch("iris_analyzer.cli.run_optimization_pipeline", return_value=capture),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            code = main(["analyze", str(self.source)])

        self.assertEqual(code, 0)
        self.assertTrue((expected / "manifest.json").is_file())
        self.assertIn(str(expected.resolve()), stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_expected_failures_are_readable_without_tracebacks(self) -> None:
        cases = []

        missing = self.root / "missing.c"
        cases.append((["analyze", str(missing)], None, "does not exist"))
        wrong = self.root / "wrong.txt"
        wrong.write_text("text\n", encoding="utf-8")
        cases.append((["analyze", str(wrong)], None, "lower-case .c"))
        cases.append(
            (
                ["analyze", str(self.source), "--max-snapshots", "0"],
                None,
                "positive integer",
            )
        )
        cases.append(
            (
                ["analyze", str(self.source), "--output", str(self.output)],
                CompilerError("Clang executable not found: missing-clang"),
                "Clang executable not found",
            )
        )

        for index, (argv, compiler_error, expected) in enumerate(cases):
            with self.subTest(index=index):
                stdout = io.StringIO()
                stderr = io.StringIO()
                if compiler_error is None:
                    context = patch("iris_analyzer.cli.resolve_clang", return_value=self.clang.resolve())
                else:
                    context = patch("iris_analyzer.cli.resolve_clang", side_effect=compiler_error)
                with context, redirect_stdout(stdout), redirect_stderr(stderr):
                    code = main(argv)
                self.assertNotEqual(code, 0)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(expected, stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())

    def test_compiler_parser_and_report_failures_are_bounded(self) -> None:
        failure_cases = [
            (CompilerError("Clang failed with exit code 1: bad C"), None, "bad C"),
            (None, CompilerOutput(self.clang, (str(self.clang),), "ordinary diagnostic\n"), "no LLVM IR"),
        ]
        for index, (compiler_error, result, expected) in enumerate(failure_cases):
            with self.subTest(index=index):
                stdout = io.StringIO()
                stderr = io.StringIO()
                run_patch = (
                    patch("iris_analyzer.cli.run_optimization_pipeline", side_effect=compiler_error)
                    if compiler_error
                    else patch("iris_analyzer.cli.run_optimization_pipeline", return_value=result)
                )
                with (
                    patch("iris_analyzer.cli.resolve_clang", return_value=self.clang.resolve()),
                    run_patch,
                    redirect_stdout(stdout),
                    redirect_stderr(stderr),
                ):
                    code = main(["analyze", str(self.source), "--output", str(self.output)])
                self.assertNotEqual(code, 0)
                self.assertIn(expected, stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())

    def test_non_empty_output_is_unchanged_on_failure(self) -> None:
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")
        with (
            patch("iris_analyzer.cli.resolve_clang", return_value=self.clang.resolve()),
            patch("iris_analyzer.cli.run_optimization_pipeline", return_value=self.successful_capture()),
        ):
            code, stdout, stderr = self.invoke()

        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("not empty", stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")


if __name__ == "__main__":
    unittest.main()
