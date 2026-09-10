# IRis Implementation Plan

## Architecture

```text
C source file
    ↓
CLI validation
    ↓
Clang runner (`-O1 -mllvm -print-after-all`)
    ↓ stderr pass dump
Snapshot parser
    ↓ structured snapshots
Change filter (per IR scope)
    ↓ retained transformations
Report writer
    ├── manifest.json
    ├── timeline.md
    └── snapshots/*.ll
```

The Phase 1 implementation is one Python package with no service, database, or runtime dependency beyond Python and Clang.

## Phase 1 — CLI Transformation Pipeline

**Goal:** Deliver a working end-to-end analyzer that converts a C file into an inspectable LLVM pass timeline.

### Work items

1. Scaffold a Python package, module entry point, and console command.
2. Add input validation and safe Clang discovery/execution.
3. Parse LLVM `IR Dump After ...` sections into typed snapshots.
4. Retain only changed snapshots within the same function/module scope.
5. Write JSON, Markdown, and LLVM IR artifacts using stable filenames.
6. Add a small loop example, user documentation, and standard-library tests.
7. Run unit tests and a real local-Clang smoke test.

### Acceptance checks

- One command analyzes `examples/loop.c`.
- The result identifies ordered pass names and their scopes.
- Repeated unchanged IR does not flood the report.
- The output directory can be removed and regenerated safely by choosing a new or overwrite-enabled destination.
- Errors identify the failed precondition or compiler diagnostic.

## Phase 2 — Explain and Compare

**Goal:** Help non-experts understand what each retained transformation did.

### Work items

- Compute line-level additions and removals for comparable snapshots.
- Add a small curated pass-description catalog.
- Generate unified diff artifacts.
- Add pass/function filters and report summary totals.

## Phase 3 — Visual Timeline

**Goal:** Turn generated reports into a polished hackathon demonstration.

### Work items

- Build a local single-page report viewer.
- Add a clickable pass timeline and side-by-side IR panes.
- Highlight added and removed lines.
- Package a pre-generated demonstration report and a short presentation flow.

## Technical Choices

| Area | Choice | Reason |
|------|--------|--------|
| Language | Python 3.10+ | Fast to build, portable, easy for faculty to follow |
| Compiler interface | Clang subprocess | Uses the real LLVM pipeline without linking LLVM libraries |
| Data model | Dataclasses | Clear typed structures with no dependency |
| Report format | JSON + Markdown + `.ll` | Machine-readable and immediately inspectable |
| Tests | `unittest` | Included with Python; no setup burden |
| Phase 3 UI | Static local web page | Sufficient for demo; no backend framework required |

## Verification Strategy

- Fixture tests for parser banner variants and malformed input.
- Unit tests for per-scope change filtering and filename sanitization.
- Temporary-directory tests for complete report output.
- CLI tests for validation and exit codes.
- Conditional smoke test with the locally discovered Clang executable.

## Deliberate Simplicity

The first release does not select arbitrary pass pipelines, execute user binaries, interpret optimization profitability, or support GPU/MLIR flows. Those features would expand the project beyond the simple explainability story that makes P01 attractive.
