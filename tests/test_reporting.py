from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iris_analyzer.model import CompilerOutput, IRSnapshot
from iris_analyzer.reporting import sanitize_component, write_report


class SanitizeComponentTests(unittest.TestCase):
    def test_normalizes_untrusted_pass_names_to_bounded_ascii(self) -> None:
        component = sanitize_component("../../Évil Pass\\Name?! " + ("X" * 100))

        self.assertRegex(component, r"^[a-z0-9-]+$")
        self.assertLessEqual(len(component), 48)
        self.assertNotIn("..", component)
        self.assertNotIn("/", component)
        self.assertNotIn("\\", component)

    def test_uses_a_stable_fallback_for_punctuation_only_names(self) -> None:
        self.assertEqual(sanitize_component("../?!"), "pass")


class WriteReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshots = [
            IRSnapshot(
                order=4,
                pass_name="InstCombine/../Pass",
                scope="sum",
                ir="define i32 @sum() {\n  ret i32 1\n}\n",
            ),
            IRSnapshot(
                order=8,
                pass_name="InstCombine/../Pass",
                scope="[module]",
                ir="define i32 @sum() {\n  ret i32 2\n}\n",
            ),
        ]
        self.compiler_output = CompilerOutput(
            clang_path=Path("/toolchain/bin/clang"),
            command=("/toolchain/bin/clang", "-O1", "input.c"),
            dump_text="unused by report writer",
        )

    def write(self, destination: Path):
        return write_report(
            destination=destination,
            source=Path("/project/input.c"),
            compiler_output=self.compiler_output,
            captured_count=9,
            snapshots=self.snapshots,
            max_snapshots=2,
            truncated=True,
        )

    def test_creates_manifest_timeline_and_numbered_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "report"

            paths = self.write(destination)

            self.assertEqual(paths.root, destination.resolve())
            self.assertTrue(paths.manifest.is_file())
            self.assertTrue(paths.timeline.is_file())
            snapshot_files = sorted(paths.snapshots_dir.glob("*.ll"))
            self.assertEqual(
                [path.name for path in snapshot_files],
                ["001-instcombine-pass.ll", "002-instcombine-pass.ll"],
            )
            self.assertEqual(snapshot_files[0].read_text(encoding="utf-8"), self.snapshots[0].ir)
            self.assertEqual(snapshot_files[1].read_text(encoding="utf-8"), self.snapshots[1].ir)

            manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
            self.assertEqual(
                set(manifest),
                {
                    "schema_version",
                    "source",
                    "clang",
                    "optimization_level",
                    "command",
                    "captured_count",
                    "retained_count",
                    "max_snapshots",
                    "truncated",
                    "snapshots",
                },
            )
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["source"], "/project/input.c")
            self.assertEqual(manifest["clang"], "/toolchain/bin/clang")
            self.assertEqual(manifest["optimization_level"], "O1")
            self.assertEqual(manifest["command"], list(self.compiler_output.command))
            self.assertEqual(manifest["captured_count"], 9)
            self.assertEqual(manifest["retained_count"], 2)
            self.assertEqual(manifest["max_snapshots"], 2)
            self.assertTrue(manifest["truncated"])
            self.assertEqual(
                manifest["snapshots"],
                [
                    {
                        "file": "snapshots/001-instcombine-pass.ll",
                        "index": 1,
                        "pass_name": "InstCombine/../Pass",
                        "scope": "sum",
                    },
                    {
                        "file": "snapshots/002-instcombine-pass.ll",
                        "index": 2,
                        "pass_name": "InstCombine/../Pass",
                        "scope": "[module]",
                    },
                ],
            )
            for item in manifest["snapshots"]:
                linked = paths.root / item["file"]
                self.assertTrue(linked.is_file())
                self.assertEqual(linked.parent, paths.snapshots_dir)

            timeline = paths.timeline.read_text(encoding="utf-8")
            self.assertLess(timeline.index("InstCombine/../Pass"), timeline.rindex("InstCombine/../Pass"))
            self.assertIn("sum", timeline)
            self.assertIn("[module]", timeline)
            self.assertIn("snapshots/001-instcombine-pass.ll", timeline)
            self.assertIn("snapshots/002-instcombine-pass.ll", timeline)

    def test_equivalent_writes_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = self.write(Path(directory) / "first")
            second = self.write(Path(directory) / "second")

            first_files = {
                path.relative_to(first.root).as_posix(): path.read_bytes()
                for path in first.root.rglob("*")
                if path.is_file()
            }
            second_files = {
                path.relative_to(second.root).as_posix(): path.read_bytes()
                for path in second.root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(first_files, second_files)

    def test_accepts_an_existing_empty_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "report"
            destination.mkdir()

            paths = self.write(destination)

            self.assertTrue(paths.manifest.is_file())

    def test_rejects_a_non_empty_destination_without_changing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "report"
            destination.mkdir()
            sentinel = destination / "keep.txt"
            sentinel.write_text("do not replace\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not empty"):
                self.write(destination)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not replace\n")
            self.assertEqual(list(destination.iterdir()), [sentinel])

    def test_write_failure_never_publishes_a_partial_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            for existing in (False, True):
                with self.subTest(existing=existing):
                    destination = parent / f"report-{existing}"
                    if existing:
                        destination.mkdir()

                    with patch(
                        "iris_analyzer.reporting._write_text",
                        side_effect=OSError("disk full"),
                    ):
                        with self.assertRaisesRegex(OSError, "disk full"):
                            self.write(destination)

                    if existing:
                        self.assertTrue(destination.is_dir())
                        self.assertEqual(list(destination.iterdir()), [])
                    else:
                        self.assertFalse(destination.exists())
                    self.assertEqual(
                        list(parent.glob(f".{destination.name}.staging-*")), []
                    )


if __name__ == "__main__":
    unittest.main()
