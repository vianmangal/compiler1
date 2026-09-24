---
phase: 01-cli-transformation-pipeline
reviewed: 2026-09-24T05:34:12Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - README.md
  - examples/loop.c
  - iris_analyzer/__init__.py
  - iris_analyzer/__main__.py
  - iris_analyzer/cli.py
  - iris_analyzer/compiler.py
  - iris_analyzer/model.py
  - iris_analyzer/parser.py
  - iris_analyzer/reporting.py
  - tests/test_cli.py
  - tests/test_compiler.py
  - tests/test_integration.py
  - tests/test_parser.py
  - tests/test_reporting.py
findings:
  critical: 1
  warning: 3
  info: 0
  total: 4
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-09-24T05:34:12Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

The CLI, report writer, compiler boundary, parser, example, and all automated tests were reviewed. The 40-test suite passes, including the local-Clang integration test, but a real trace demonstrates that the central changed-pass timeline is not trustworthy: the same-scope comparison attributes changes made by intervening nested passes to later no-op passes and discards the first real change observed for every textual scope. Three additional robustness and test-reliability issues should also be corrected.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01 [BLOCKER]: Same-scope snapshots do not identify which pass caused a change

**File:** `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/parser.py:86-98`

**Related:** `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/compiler.py:42-52`, `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/cli.py:108-111`

**Issue:** `retain_changed` compares the current dump with the last dump carrying the same scope label, not with the IR immediately before that pass ran. LLVM interleaves module, function, and loop pass dumps. A function pass can therefore mutate a function between two `[module]` dumps; the next module pass is then reported as the cause even when that module pass made no change. The first snapshot for every textual scope is also always discarded, even if that first pass changed the IR. Scope spelling changes such as `main` versus `(main)` make the false-negative/false-positive behavior worse.

This is reproducible with the checked-in `examples/loop.c` on Apple Clang 21. The generated report claims that `OpenMPOptPass`, `AlwaysInlinerPass`, `DeadArgumentEliminationPass`, and `HotColdSplittingPass` changed the program, while the same compiler's `-mllvm -print-changed` output marks those passes as “omitted because no change.” Conversely, `InlinerPass on (main)` is marked changed by Clang but is discarded as that scope's baseline; the following unchanged `PostOrderFunctionAttrsPass on (main)` is reported instead. This violates the project's core promise to show which passes actually changed the IR.

**Fix:** Capture each pass's own before/after state or use LLVM's changed-pass instrumentation when supported. Do not infer causality from non-adjacent snapshots sharing a scope label. For example, capability-detect `-mllvm -print-changed`, parse only non-omitted `IR Dump After` sections, and cap those already-classified changes directly:

```python
changed = parse_changed_dumps(compiler_output.dump_text)
retained = changed[:max_snapshots]
truncated = len(changed) > max_snapshots
```

For toolchains without `-print-changed`, request paired `-print-before-all` and `-print-after-all` dumps and compare the before/after pair for the same pass invocation. Add regression coverage for nested module/function/loop interleaving and for the first changed event in a scope.

## Warnings

### WR-01 [WARNING]: The snapshot cap does not bound compiler-output memory

**File:** `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/compiler.py:54-63`

**Related:** `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/parser.py:30-71`, `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/cli.py:108-111`

**Issue:** `subprocess.run(..., stderr=PIPE, text=True)` buffers the entire `-print-after-all` stream, `parse_ir_dumps` then materializes every complete IR snapshot, and only afterward does `retain_changed` apply `--max-snapshots`. Because `-print-after-all` repeats large IR bodies for many passes, a valid but larger C input can exhaust memory before either the 30-second timeout or the retention cap provides protection. Even failure diagnostics are bounded only after all stderr has already been captured.

**Fix:** Stream stderr with `subprocess.Popen`, parse dump boundaries incrementally, and enforce a hard byte/snapshot-input ceiling. Continue draining or terminate the compiler cleanly once the limit is exceeded, then raise a readable `CompilerError`. Using `-print-changed` for CR-01 will reduce output volume but should not replace an explicit byte bound.

### WR-02 [WARNING]: A failed write leaves a poisoned, non-empty report directory

**File:** `/Users/vian/Documents/ChatGPT/compiler-lab/iris_analyzer/reporting.py:44-110`

**Issue:** `write_report` creates the destination and `snapshots/` before writing artifacts one by one. If a snapshot, manifest, or timeline write fails because of an I/O error, encoding error, or exhausted disk, the CLI returns an error but leaves a partial non-empty directory. Retrying the same command then fails the non-empty-directory guard, and consumers may mistake the partial directory for a completed report.

**Fix:** Build the complete report in a temporary sibling directory and publish it only after every file succeeds, using a same-filesystem rename/replace that preserves the existing empty/non-empty destination policy. Always remove the staging directory on failure. Add an injected-write-failure test asserting that no partial report is published.

### WR-03 [WARNING]: The passing tests do not verify pass attribution

**File:** `/Users/vian/Documents/ChatGPT/compiler-lab/tests/test_parser.py:137-163`

**Related:** `/Users/vian/Documents/ChatGPT/compiler-lab/tests/test_integration.py:51-67`

**Issue:** The parser test models scopes as independent strings and therefore encodes the flawed assumption behind CR-01. The real-Clang test asserts only that at least two entries and their files exist. It passes even though the produced timeline contains multiple confirmed no-op passes and omits a confirmed changed pass, so the suite cannot verify the project's core value.

**Fix:** Add a regression fixture containing paired before/after or changed/omitted pass events across interleaved module, function, and loop scopes. Assert the exact changed-event identities, including the first changed event for a scope and exclusion of a no-op module pass following a changed function pass. Keep the integration assertions version-tolerant by deriving the expected changed events from the selected compiler's supported changed-pass output rather than hard-coding a complete pass list.

---

_Reviewed: 2026-09-24T05:34:12Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
