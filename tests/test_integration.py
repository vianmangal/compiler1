from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_SOURCE = REPOSITORY_ROOT / "examples" / "loop.c"


class LocalClangIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("clang"), "local clang is not available")
    def test_documented_example_generates_a_complete_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            working_directory = Path(directory)
            report = working_directory / "loop-report"
            environment = os.environ.copy()
            existing_pythonpath = environment.get("PYTHONPATH")
            environment["PYTHONPATH"] = (
                str(REPOSITORY_ROOT)
                if not existing_pythonpath
                else os.pathsep.join((str(REPOSITORY_ROOT), existing_pythonpath))
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "iris_analyzer",
                    "analyze",
                    str(EXAMPLE_SOURCE),
                    "--output",
                    str(report),
                    "--max-snapshots",
                    "25",
                ],
                cwd=working_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stderr, "")
            self.assertIn("Retained ", completed.stdout)
            self.assertIn(str(report.resolve()), completed.stdout)
            self.assertTrue((report / "manifest.json").is_file())
            self.assertTrue((report / "timeline.md").is_file())

            manifest = json.loads((report / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["optimization_level"], "O1")
            self.assertGreaterEqual(manifest["retained_count"], 2)
            self.assertLessEqual(manifest["retained_count"], 25)
            self.assertEqual(manifest["retained_count"], len(manifest["snapshots"]))
            for snapshot in manifest["snapshots"]:
                artifact = report / snapshot["file"]
                self.assertTrue(artifact.is_file())
                self.assertEqual(artifact.parent, report / "snapshots")


if __name__ == "__main__":
    unittest.main()
