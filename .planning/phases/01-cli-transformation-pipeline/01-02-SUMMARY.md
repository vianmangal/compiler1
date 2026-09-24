---
phase: 01-cli-transformation-pipeline
plan: 02
subsystem: cli-reporting
tags: [python, clang, llvm-ir, argparse, json, unittest]
requires:
  - phase: 01-cli-transformation-pipeline-01
    provides: Typed LLVM snapshots, per-scope change filtering, and safe Clang capture
provides:
  - One-command C-to-LLVM-transformation-report workflow
  - Deterministic JSON, Markdown, and numbered LLVM IR artifacts
  - Validated CLI errors, a documented loop example, and real-Clang smoke coverage
affects: [phase-2-explanations, phase-3-visualization, hackathon-demo]
tech-stack:
  added: [Python argparse, Python json, standard-library integration testing]
  patterns: [safe report directories, sanitized artifact names, concise domain errors]
key-files:
  created:
    - iris_analyzer/reporting.py
    - iris_analyzer/cli.py
    - iris_analyzer/__main__.py
    - tests/test_reporting.py
    - tests/test_cli.py
    - tests/test_integration.py
    - examples/loop.c
  modified:
    - README.md
    - iris_analyzer/parser.py
    - tests/test_parser.py
key-decisions:
  - "Reject non-empty report destinations instead of deleting or overwriting user files."
  - "Use a global positive retained-snapshot cap while preserving per-scope comparison semantics."
  - "Accept both plain and LLVM comment-prefixed pass-dump banners for local Clang compatibility."
patterns-established:
  - "CLI boundary: map expected validation, compiler, parser, and report failures to concise stderr and exit code 2."
  - "Report boundary: derive filenames only from bounded sanitized ASCII components plus stable ordinals."
requirements-completed: [INPUT-01, INPUT-02, INPUT-03, CAPT-01, CAPT-02, CAPT-03, CAPT-04, RPRT-01, RPRT-02, RPRT-03, RPRT-04, QUAL-01, QUAL-02]
duration: 8min
completed: 2026-09-24
---

# Phase 1 Plan 02: CLI Transformation Pipeline Summary

**A dependency-free command now turns a local C file into a bounded, deterministic LLVM transformation report verified against Apple Clang 21**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-24T04:40:00Z
- **Completed:** 2026-09-24T04:48:13Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Added `python3 -m iris_analyzer analyze SOURCE` with exact source validation, Clang discovery/override, positive snapshot caps, and readable failure handling.
- Added deterministic `manifest.json`, `timeline.md`, and numbered sanitized `.ll` snapshot output without overwriting non-empty directories.
- Added a documented loop example and a real-Clang smoke test that retained 25 capped transformations from 169 captured snapshots on the local toolchain.
- Expanded the complete standard-library suite to 40 passing tests.

## Task Commits

Each task was committed atomically:

1. **Task 1: Generate deterministic and path-safe report artifacts** - `08530ad` (test), `f4730c7` (feat)
2. **Task 2: Wire validated CLI input through capture, filtering, and reporting** - `8f9ccea` (test), `5368ad9` (feat)
3. **Task 3: Ship the example, first-run documentation, and conditional local-Clang proof** - `98474e1` (feat)

**Plan metadata:** included in the plan close-out commit.

## Files Created/Modified

- `iris_analyzer/reporting.py` - Deterministic and path-safe report writer.
- `iris_analyzer/cli.py` - Validated analyze command and full pipeline orchestration.
- `iris_analyzer/__main__.py` - Module entry point for `python3 -m iris_analyzer`.
- `tests/test_reporting.py` - Manifest, timeline, snapshot, determinism, and destination-safety tests.
- `tests/test_cli.py` - Argument, validation, orchestration, cap, success, and error tests.
- `tests/test_integration.py` - Conditional real-Clang end-to-end test.
- `examples/loop.c` - Small warning-free optimization example.
- `README.md` - Prerequisites, command, options, output layout, safety, tests, and scope.
- `iris_analyzer/parser.py` - Compatibility with comment-prefixed real-Clang dump banners.
- `tests/test_parser.py` - Regression coverage for the local Clang banner format.

## Decisions Made

- The report writer accepts a missing or empty output directory and refuses a populated one, making regeneration explicit and safe.
- Manifest paths use POSIX-style relative links while source and compiler provenance retain their resolved values.
- An empty parsed dump is a readable command failure instead of a misleading empty success report.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Accepted LLVM comment-prefixed pass-dump banners**
- **Found during:** Task 3 (real local-Clang proof)
- **Issue:** Apple Clang 21 emitted `; *** IR Dump After ...` banners, while the existing parser accepted only unprefixed `*** IR Dump After ...` lines. The real integration run therefore found no snapshots.
- **Fix:** Allowed an optional LLVM comment marker before Before/After dump banners and added a focused regression test.
- **Files modified:** `iris_analyzer/parser.py`, `tests/test_parser.py`
- **Verification:** The regression test and real-Clang integration test pass; the complete suite passes all 40 tests.
- **Committed in:** `98474e1`

---

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** The two extra modified files were required for the promised real-Clang behavior. Scope remains limited to Phase 1 parser compatibility.

## Issues Encountered

- The first verification shell wrapper used zsh's reserved `status` variable. It was rerun with a task-specific variable; all intended checks then passed.

## User Setup Required

None beyond Python 3.10+ and a local Clang executable, both documented in the README. No external services or third-party packages are required.

## Next Phase Readiness

- Phase 1 is a complete working vertical slice and is ready for Phase 2 pass explanations, comparison metrics, and diffs.
- The manifest and stable relative snapshot links provide the data contract needed by later explanation and visualization work.

## TDD Gate Compliance

- Task 1: RED `08530ad` preceded GREEN `f4730c7`.
- Task 2: RED `8f9ccea` preceded GREEN `5368ad9`.
- Task 3 did not require a TDD gate and passed the complete real-Clang verification.

## Self-Check: PASSED

- All ten created or modified implementation, test, example, and documentation files exist.
- All five Plan 01-02 task commits exist on `main`.
- The real command retained 25 transformations from 169 captured snapshots and produced valid linked artifacts.
- Missing source, wrong extension, zero cap, invalid Clang, and non-empty output cases all return readable non-zero errors without tracebacks.
- `python3 -m compileall -q iris_analyzer tests` succeeds.
- `python3 -m unittest discover -s tests -v` passes all 40 tests, including the local-Clang integration test.

---
*Phase: 01-cli-transformation-pipeline*
*Completed: 2026-09-24*
