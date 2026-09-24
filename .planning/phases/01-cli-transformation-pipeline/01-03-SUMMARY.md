---
phase: 01-cli-transformation-pipeline
plan: 03
subsystem: compiler-capture-validation
tags: [python, clang, llvm-ir, unittest, integration-testing]
requires:
  - phase: 01-cli-transformation-pipeline-02
    provides: One-command analysis workflow and deterministic numbered LLVM snapshot reports
provides:
  - Complete module-scope changed-pass LLVM dumps
  - Exact safe-command regression coverage for both instrumentation flags
  - Real-Clang validation of every published numbered LLVM snapshot
affects: [phase-2-explanations, phase-3-visualization, report-consumers]
tech-stack:
  added: []
  patterns: [same-toolchain artifact validation, bounded subprocess diagnostics]
key-files:
  created: []
  modified:
    - iris_analyzer/compiler.py
    - tests/test_compiler.py
    - tests/test_integration.py
    - README.md
key-decisions:
  - "Preserve LLVM's changed-pass event selection and add module-scope printing at the capture source instead of repairing incomplete IR downstream."
  - "Validate every report artifact with the exact resolved Clang recorded in the run manifest."
patterns-established:
  - "Compiler contract: assert the complete ordered argument tuple for safety-critical instrumentation."
  - "Artifact contract: parse each generated LLVM file independently with bounded, path-specific failure diagnostics."
requirements-completed: [CAPT-01, CAPT-02, CAPT-03, RPRT-03, QUAL-01, QUAL-02]
duration: 9min
completed: 2026-09-24
---

# Phase 1 Plan 03: Standalone LLVM Snapshot Gap Closure Summary

**Changed-pass capture now emits complete module-scope LLVM IR, with every published snapshot independently accepted by the same resolved Clang**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-24T15:57:00Z
- **Completed:** 2026-09-24T16:06:30Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `-mllvm -print-module-scope` immediately after the retained `-mllvm -print-changed` pair while preserving the O1, shell-free, bounded, non-executing compiler boundary.
- Locked the exact Clang command ordering in focused compiler tests.
- Strengthened the real-toolchain test to parse every numbered `.ll` artifact with the manifest's resolved Clang and provide bounded artifact-specific diagnostics.
- Updated the README narrowly to document compatible instrumentation and the standalone-module snapshot guarantee.

## Task Commits

Each task was committed atomically:

1. **Task 1: Emit complete module-scope changed-pass dumps** - `ab5c492` (test), `476e3b8` (feat)
2. **Task 2: Prove every generated snapshot parses with the selected Clang** - `1c3da3a` (test/docs)

**Plan metadata:** included in the plan close-out commit.

## Files Created/Modified

- `iris_analyzer/compiler.py` - Requests changed-pass dumps as complete module-scope LLVM IR.
- `tests/test_compiler.py` - Asserts the exact safe capture command including both LLVM instrumentation pairs.
- `tests/test_integration.py` - Parses every generated snapshot with the same Clang and reports bounded diagnostics on failure.
- `README.md` - States the instrumentation prerequisite and independently parseable snapshot behavior.

## Decisions Made

- Fixed incomplete LLVM payloads at the compiler boundary rather than adding parser or report repair logic, preserving pass identity and report schema.
- Reused the compiler path recorded in `manifest.json` for artifact validation so the integration proof cannot silently switch toolchains.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The dependency audit's first allowlist omitted two existing standard-library imports (`contextlib` and `io`); the audit was corrected and confirmed there are no third-party imports.
- The first self-check loop used zsh's special `path` variable and temporarily hid executables from `PATH`; it was rerun with a task-specific variable and every file and commit was found.

## User Setup Required

None - no external service configuration or third-party package is required. A compatible local Clang remains the only documented toolchain prerequisite.

## Next Phase Readiness

- The sole Phase 1 verification gap is closed: every snapshot from the documented example is a valid standalone LLVM module.
- The stable manifest and complete snapshot artifacts are ready for Phase 2 explanation, metrics, and diff work.

## TDD Gate Compliance

- Task 1 used RED `ab5c492` followed by GREEN `476e3b8`.
- Task 2 added verification and documentation for the behavior introduced by Task 1; its focused integration and full-suite checks passed.

## Self-Check: PASSED

- All four plan-owned files exist and contain the required module-scope capture and per-artifact validation behavior.
- Task commits `ab5c492`, `476e3b8`, and `1c3da3a` exist on `main`.
- Focused compiler tests pass all 12 cases.
- The local-Clang integration test passes and validates every generated numbered snapshot.
- The complete standard-library suite passes all 45 tests.
- `python3 -m compileall -q iris_analyzer tests` succeeds.
- No third-party import, package install, report-schema change, or CLI-contract change was introduced.

---
*Phase: 01-cli-transformation-pipeline*
*Completed: 2026-09-24*
