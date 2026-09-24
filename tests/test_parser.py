from __future__ import annotations

import dataclasses
from pathlib import Path
import unittest

from iris_analyzer.model import CLIConfig, CompilerOutput, IRSnapshot, ReportPaths
from iris_analyzer.parser import normalize_ir, parse_ir_dumps, retain_changed


FIXTURES = Path(__file__).parent / "fixtures"


class ModelContractTests(unittest.TestCase):
    def test_snapshot_contract_is_frozen(self) -> None:
        snapshot = IRSnapshot(order=1, pass_name="SROAPass", scope="sum", ir="ret\n")

        with self.assertRaises(dataclasses.FrozenInstanceError):
            snapshot.order = 2  # type: ignore[misc]

    def test_supporting_contracts_expose_required_fields(self) -> None:
        clang = Path("/usr/bin/clang")
        source = Path("input.c")
        output = Path("report")

        compiler_output = CompilerOutput(
            clang_path=clang,
            command=(str(clang), "-O1"),
            dump_text="dump",
        )
        config = CLIConfig(
            source=source,
            clang_override=None,
            output_dir=output,
            max_snapshots=50,
        )
        paths = ReportPaths(
            root=output,
            manifest=output / "manifest.json",
            timeline=output / "timeline.md",
            snapshots_dir=output / "snapshots",
        )

        self.assertEqual(compiler_output.command, (str(clang), "-O1"))
        self.assertEqual(config.max_snapshots, 50)
        self.assertEqual(paths.snapshots_dir, output / "snapshots")


class ParseIRDumpsTests(unittest.TestCase):
    def test_parses_after_sections_in_stream_order(self) -> None:
        dump_text = (FIXTURES / "clang_ir_dump.txt").read_text(encoding="utf-8")

        snapshots = parse_ir_dumps(dump_text)

        self.assertEqual([snapshot.order for snapshot in snapshots], [1, 2, 3, 4])
        self.assertEqual(
            [(snapshot.pass_name, snapshot.scope) for snapshot in snapshots],
            [
                ("SROAPass", "sum"),
                ("EarlyCSEPass", "[module]"),
                ("InstCombinePass", "sum"),
                ("NoOpPass", "sum"),
            ],
        )
        self.assertEqual(
            snapshots[0].ir,
            "define i32 @sum(i32 %value) {\n"
            "entry:\n"
            "  %added = add i32 %value, %value\n"
            "  ret i32 %added\n"
            "}\n",
        )
        self.assertNotIn("@before", "".join(snapshot.ir for snapshot in snapshots))
        self.assertNotIn("clang: note", "".join(snapshot.ir for snapshot in snapshots))

    def test_accepts_banner_variants_and_ignores_malformed_sections(self) -> None:
        dump_text = (FIXTURES / "clang_ir_dump_variants.txt").read_text(
            encoding="utf-8"
        )

        snapshots = parse_ir_dumps(dump_text)

        self.assertEqual(
            [(snapshot.pass_name, snapshot.scope) for snapshot in snapshots],
            [
                ("SimplifyCFGPass", "function (helper)"),
                ("GlobalDCEPass", "[module]"),
            ],
        )
        all_ir = "".join(snapshot.ir for snapshot in snapshots)
        self.assertNotIn("must_not_parse", all_ir)
        self.assertNotIn("before_only", all_ir)

    def test_empty_input_has_no_snapshots(self) -> None:
        self.assertEqual(parse_ir_dumps("ordinary diagnostic\n"), [])

    def test_accepts_real_clang_comment_prefixed_banners(self) -> None:
        dump_text = (
            "; *** IR Dump After Annotation2MetadataPass on [module] ***\n"
            "; ModuleID = 'input.c'\n"
            "define i32 @main() {\n"
            "  ret i32 0\n"
            "}\n"
            "; *** IR Dump After InstCombinePass on main ***\n"
            "define i32 @main() {\n"
            "  ret i32 1\n"
            "}\n"
        )

        snapshots = parse_ir_dumps(dump_text)

        self.assertEqual(
            [(snapshot.pass_name, snapshot.scope) for snapshot in snapshots],
            [("Annotation2MetadataPass", "[module]"), ("InstCombinePass", "main")],
        )


class NormalizeIRTests(unittest.TestCase):
    def test_normalizes_line_endings_and_trailing_whitespace(self) -> None:
        crlf = "define void @f() {  \r\n  ret void\t\r\n}\r\n\r\n"
        lf = "define void @f() {\n  ret void\n}\n"

        self.assertEqual(normalize_ir(crlf), normalize_ir(lf))

    def test_preserves_semantic_text_changes(self) -> None:
        self.assertNotEqual(
            normalize_ir("ret i32 1\n"),
            normalize_ir("ret i32 2\n"),
        )


class RetainChangedTests(unittest.TestCase):
    @staticmethod
    def snapshot(order: int, pass_name: str, scope: str, ir: str) -> IRSnapshot:
        return IRSnapshot(order=order, pass_name=pass_name, scope=scope, ir=ir)

    def setUp(self) -> None:
        self.snapshots = [
            self.snapshot(1, "FirstChangeA", "a", "ret i32 1\n"),
            self.snapshot(2, "ChangeB", "b", "ret i32 9\n"),
            self.snapshot(3, "SecondChangeA", "a", "ret i32 2\n"),
        ]

    def test_keeps_first_changed_event_and_preserves_global_order(self) -> None:
        retained, truncated = retain_changed(self.snapshots, max_snapshots=10)

        self.assertEqual([snapshot.order for snapshot in retained], [1, 2, 3])
        self.assertFalse(truncated)

    def test_caps_changed_snapshots_and_reports_actual_truncation(self) -> None:
        retained, truncated = retain_changed(self.snapshots, max_snapshots=1)

        self.assertEqual([snapshot.order for snapshot in retained], [1])
        self.assertTrue(truncated)

    def test_exact_cap_is_not_reported_as_truncated(self) -> None:
        retained, truncated = retain_changed(self.snapshots[:1], max_snapshots=1)

        self.assertEqual([snapshot.order for snapshot in retained], [1])
        self.assertFalse(truncated)

    def test_requires_a_positive_cap(self) -> None:
        for invalid in (0, -1):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "positive"):
                    retain_changed(self.snapshots, max_snapshots=invalid)

    def test_parser_excludes_omitted_events_across_interleaved_scopes(self) -> None:
        dump_text = """\
*** IR Dump After NoOpModulePass on [module] omitted because no change ***
*** IR Dump After FirstFunctionChange on (main) ***
define i32 @main() { ret i32 1 }
*** IR Dump After LaterNoOpFunctionPass on (main) omitted because no change ***
*** IR Dump After LoopChangePass on loop %for.body in function main ***
define i32 @main() { ret i32 2 }
*** IR Dump After FollowingNoOpModulePass on [module] omitted because no change ***
"""

        snapshots = parse_ir_dumps(dump_text)
        retained, truncated = retain_changed(snapshots, max_snapshots=10)

        self.assertEqual(
            [(item.pass_name, item.scope) for item in retained],
            [
                ("FirstFunctionChange", "(main)"),
                ("LoopChangePass", "loop %for.body in function main"),
            ],
        )
        self.assertFalse(truncated)


if __name__ == "__main__":
    unittest.main()
