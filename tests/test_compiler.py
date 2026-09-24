from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import ANY, patch

from iris_analyzer.compiler import CompilerError, resolve_clang, run_optimization_pipeline


class ResolveClangTests(unittest.TestCase):
    def make_executable(self, directory: str, name: str = "clang") -> Path:
        candidate = Path(directory) / name
        candidate.write_text("#!/bin/sh\n", encoding="utf-8")
        candidate.chmod(candidate.stat().st_mode | stat.S_IXUSR)
        return candidate

    def test_discovers_default_clang_from_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = self.make_executable(directory)
            with patch("iris_analyzer.compiler.shutil.which", return_value=str(candidate)) as which:
                resolved = resolve_clang(None)

        which.assert_called_once_with("clang")
        self.assertEqual(resolved, candidate.resolve())

    def test_resolves_an_explicit_command_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = self.make_executable(directory, "custom-clang")
            with patch("iris_analyzer.compiler.shutil.which", return_value=str(candidate)) as which:
                resolved = resolve_clang("custom-clang")

        which.assert_called_once_with("custom-clang")
        self.assertEqual(resolved, candidate.resolve())

    def test_resolves_an_explicit_executable_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = self.make_executable(directory)

            resolved = resolve_clang(str(candidate))

        self.assertEqual(resolved, candidate.resolve())

    def test_rejects_missing_compiler(self) -> None:
        with patch("iris_analyzer.compiler.shutil.which", return_value=None):
            with self.assertRaisesRegex(CompilerError, "not found"):
                resolve_clang("missing-clang")

    def test_rejects_directory_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch("iris_analyzer.compiler.shutil.which", return_value=directory):
                with self.assertRaisesRegex(CompilerError, "regular file"):
                    resolve_clang("clang")

    def test_rejects_non_executable_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "clang"
            candidate.write_text("not executable\n", encoding="utf-8")
            candidate.chmod(stat.S_IRUSR | stat.S_IWUSR)
            with patch("iris_analyzer.compiler.shutil.which", return_value=str(candidate)):
                with self.assertRaisesRegex(CompilerError, "not executable"):
                    resolve_clang("clang")


class RunOptimizationPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        root = Path(self.temp_directory.name)
        self.source = root / "program.c"
        self.source.write_text("int main(void) { return 0; }\n", encoding="utf-8")
        self.clang = root / "clang"
        self.clang.write_text("#!/bin/sh\n", encoding="utf-8")
        self.clang.chmod(self.clang.stat().st_mode | stat.S_IXUSR)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    @property
    def expected_command(self) -> tuple[str, ...]:
        return (
            str(self.clang.resolve()),
            "-O1",
            "-S",
            "-emit-llvm",
            "-mllvm",
            "-print-changed",
            str(self.source.resolve()),
            "-o",
            os.devnull,
        )

    class FakeProcess:
        def __init__(self, returncode: int | None) -> None:
            self.returncode = returncode
            self.terminated = False
            self.killed = False

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.terminated = True
            self.returncode = -15

        def wait(self, timeout: int | None = None) -> int:
            assert self.returncode is not None
            return self.returncode

        def kill(self) -> None:
            self.killed = True
            self.returncode = -9

    def popen_result(self, stderr: str, returncode: int | None = 0):
        process = self.FakeProcess(returncode)

        def launch(*args, **kwargs):
            stream = kwargs["stderr"]
            stream.write(stderr.encode("utf-8"))
            stream.flush()
            return process

        return process, launch

    def test_invokes_exact_safe_pipeline_and_returns_capture(self) -> None:
        stderr = "*** IR Dump After InstCombinePass on main ***\nret i32 0\n"
        _, launch = self.popen_result(stderr)
        with patch("iris_analyzer.compiler.subprocess.Popen", side_effect=launch) as popen:
            output = run_optimization_pipeline(self.source, self.clang)

        popen.assert_called_once_with(
            self.expected_command,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=ANY,
        )
        self.assertEqual(output.clang_path, self.clang.resolve())
        self.assertEqual(output.command, self.expected_command)
        self.assertEqual(output.dump_text, stderr)

    def test_maps_nonzero_exit_to_bounded_domain_error(self) -> None:
        _, launch = self.popen_result(
            "fatal: invalid source\n" + ("x" * 10_000), returncode=2
        )
        with patch("iris_analyzer.compiler.subprocess.Popen", side_effect=launch):
            with self.assertRaises(CompilerError) as caught:
                run_optimization_pipeline(self.source, self.clang)

        message = str(caught.exception)
        self.assertIn("exit code 2", message)
        self.assertIn("fatal: invalid source", message)
        self.assertLess(len(message), 5_000)

    def test_explains_missing_changed_pass_instrumentation(self) -> None:
        _, launch = self.popen_result(
            "clang (LLVM option parsing): Unknown command line argument "
            "'-print-changed'",
            returncode=1,
        )
        with patch("iris_analyzer.compiler.subprocess.Popen", side_effect=launch):
            with self.assertRaisesRegex(
                CompilerError, "does not support.*-print-changed"
            ):
                run_optimization_pipeline(self.source, self.clang)

    def test_maps_timeout_to_distinguishable_domain_error(self) -> None:
        process = self.FakeProcess(None)
        with (
            patch("iris_analyzer.compiler.subprocess.Popen", return_value=process),
            patch("iris_analyzer.compiler.time.monotonic", side_effect=[0.0, 31.0]),
        ):
            with self.assertRaisesRegex(CompilerError, "timed out after 30 seconds"):
                run_optimization_pipeline(self.source, self.clang)
        self.assertTrue(process.terminated)

    def test_rejects_oversized_pass_output_and_stops_compiler(self) -> None:
        process, launch = self.popen_result("x" * 33, returncode=None)
        with (
            patch("iris_analyzer.compiler.subprocess.Popen", side_effect=launch),
            patch("iris_analyzer.compiler._MAX_DUMP_BYTES", 32),
        ):
            with self.assertRaisesRegex(CompilerError, "safety limit"):
                run_optimization_pipeline(self.source, self.clang)
        self.assertTrue(process.terminated)

    def test_maps_launch_failure_to_domain_error(self) -> None:
        with patch(
            "iris_analyzer.compiler.subprocess.Popen",
            side_effect=OSError("permission changed"),
        ):
            with self.assertRaisesRegex(CompilerError, "Could not run Clang"):
                run_optimization_pipeline(self.source, self.clang)


if __name__ == "__main__":
    unittest.main()
