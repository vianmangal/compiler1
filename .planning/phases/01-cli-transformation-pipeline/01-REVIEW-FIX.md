---
phase: 01-cli-transformation-pipeline
fixed_at: 2026-09-24T05:52:41Z
review_path: .planning/phases/01-cli-transformation-pipeline/01-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 1: Code Review Fix Report

**Fixed at:** 2026-09-24T05:52:41Z
**Source review:** `.planning/phases/01-cli-transformation-pipeline/01-REVIEW.md`
**Iteration:** 1

**Summary:**

- Findings in scope: 4
- Fixed: 4
- Skipped: 0
- Verification: 44 tests passed, including the real local-Clang integration

## Fixed Issues

### CR-01: Same-scope snapshots do not identify which pass caused a change

**Status:** fixed: requires human verification
**Files modified:** `iris_analyzer/compiler.py`, `iris_analyzer/parser.py`, `tests/test_compiler.py`, `tests/test_parser.py`, `tests/test_cli.py`
**Commit:** 15377de
**Applied fix:** Changed the compiler boundary to request LLVM's `-print-changed` instrumentation, excluded events explicitly marked as no-ops, retained the first real changed event, and capped the already-classified changed stream directly. Unsupported toolchains now fail with a clear compatibility error instead of silently using unsound attribution.

### WR-01: The snapshot cap does not bound compiler-output memory

**Status:** fixed
**Files modified:** `iris_analyzer/compiler.py`, `tests/test_compiler.py`
**Commit:** 2cfb86b
**Applied fix:** Replaced whole-output `subprocess.run` capture with `Popen` streaming to a temporary file, enforced a 16 MiB pass-output ceiling and the existing 30-second timeout, and terminated the compiler when either resource boundary is crossed.

### WR-02: A failed write leaves a poisoned, non-empty report directory

**Status:** fixed
**Files modified:** `iris_analyzer/reporting.py`, `tests/test_reporting.py`
**Commit:** 9fe4c9e
**Applied fix:** The writer now builds the complete report in a temporary sibling directory and atomically publishes it only after every artifact succeeds. Failed writes remove staging data and preserve an existing empty destination.

### WR-03: The passing tests do not verify pass attribution

**Status:** fixed
**Files modified:** `tests/test_integration.py`
**Commit:** 6aac6ac
**Applied fix:** The real-Clang integration test now independently derives changed pass/scope identities from LLVM's raw `-print-changed` output and requires the manifest timeline to match exactly. The CR-01 regression test also covers interleaved scopes, the first changed event, and exclusion of following no-op passes.

---

_Fixed: 2026-09-24T05:52:41Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
