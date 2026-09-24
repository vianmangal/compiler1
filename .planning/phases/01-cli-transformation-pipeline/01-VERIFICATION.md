---
phase: 01-cli-transformation-pipeline
verified: 2026-09-24T16:14:55Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 7/8
  gaps_closed:
    - "Every retained transformation is published as a valid, standalone numbered LLVM .ll snapshot"
  gaps_remaining: []
  regressions: []
---

# Phase 1: CLI Transformation Pipeline Verification Report

**Phase Goal:** Users can run one command to convert a local C file into a trustworthy timeline of the LLVM passes that changed its IR.
**Verified:** 2026-09-24T16:14:55Z
**Status:** passed
**Re-verification:** Yes — after standalone LLVM snapshot gap closure

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A user can analyze exactly one existing `.c` file with the module command, PATH Clang, or an explicit `--clang` override. | ✓ VERIFIED | `iris_analyzer/cli.py:35-72,75-120`; the fresh documented command exited 0 with PATH Clang, while focused tests cover the explicit override. |
| 2 | Invalid source, extension, toolchain, compilation, cap, or report destination produces a concise non-zero error without a traceback. | ✓ VERIFIED | `iris_analyzer/cli.py:75-85,121-125`; the full suite covers every bounded error class, and a fresh missing-source invocation exited 2 with a single concise diagnostic. |
| 3 | The real LLVM `-O1` capture reports ordered pass names and scopes corresponding exactly to LLVM's changed-pass instrumentation. | ✓ VERIFIED | `iris_analyzer/compiler.py:42-59` uses `-O1`, `-print-changed`, and `-print-module-scope`. An independent fresh raw capture produced 21 changed events and all 21 manifest `(pass_name, scope)` identities matched in exact order. |
| 4 | Retained output is bounded by a positive configurable cap and compiler capture has explicit time and byte limits. | ✓ VERIFIED | `iris_analyzer/parser.py:82-99` enforces the cap; `compiler.py:16-19,61-92` enforces 30 seconds and 16 MiB. A fresh cap-2 run retained exactly 2 and set `truncated=true`; focused timeout/output-limit tests pass. |
| 5 | A successful run publishes deterministic `manifest.json`, `timeline.md`, and numbered path-safe standalone `.ll` files transactionally. | ✓ VERIFIED | `reporting.py:35-75,78-84,87-173` stages then atomically publishes the complete tree. The fresh run produced 21 linked `.ll` files, and all 21 parsed successfully with the manifest's exact `/usr/bin/clang`. |
| 6 | Manifest, timeline, and terminal output agree on retained order/count and identify the report location. | ✓ VERIFIED | The fresh run printed the absolute report path and retained count; 21/21 manifest entries matched timeline identities and links, and every link resolved under `snapshots/`. |
| 7 | A first-time user can follow the README to analyze the included example. | ✓ VERIFIED | `README.md:5-68` documents prerequisites, exact first-run command, flags, output contract, and test command. The documented example completed successfully against local Clang. |
| 8 | Maintainers can verify parser, compiler, reporting, CLI, standalone artifacts, and local-Clang behavior with the standard-library suite. | ✓ VERIFIED | `python3 -m unittest discover -s tests -v` ran 45 tests with 45 passing, including the real local-Clang test that validates every numbered snapshot. `python3 -m compileall -q iris_analyzer tests` also passed. |

**Score:** 8/8 truths verified

### Plan Must-Have Coverage

| Plan | Must-have truths | Status | Evidence |
|------|------------------|--------|----------|
| 01-01 | Typed ordered snapshots, changed-only bounded retention, safe real-Clang capture, bounded failures | ✓ VERIFIED | Immutable contracts and parser/compiler boundaries exist and are wired; focused parser/compiler tests pass. The original lexical `-print-after-all` key-link was intentionally superseded by the reviewed `-print-changed` implementation, which directly implements the goal's changed-pass contract and is independently identity-checked. |
| 01-02 | One-command validated CLI, readable failures, real bounded capture, deterministic report, terminal summary and documented example | ✓ VERIFIED | The fresh CLI run, missing-source run, cap-2 run, report inspection, README, and full suite collectively verify all five truths. |
| 01-03 | Complete standalone modules, preserved safe command, exact-command regression test, per-artifact same-Clang validation | ✓ VERIFIED | `compiler.py:47-68`; `tests/test_compiler.py:81-143`; `tests/test_integration.py:82-133`; fresh independent result: `standalone_valid=21/21`. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `iris_analyzer/model.py` | Frozen pipeline data contracts | ✓ VERIFIED | Exists, substantive, imported by parser/compiler/CLI/reporting, and exercised by tests. |
| `iris_analyzer/parser.py` | Changed-event parsing, clean boundaries, and bounded retention | ✓ VERIFIED | Opens only changed `IR Dump After` events, terminates on all dump/pass banners, emits ordered typed bodies, and caps output. Fresh artifacts contain no event banners. |
| `iris_analyzer/compiler.py` | Safe real-Clang O1 module-scope changed-event capture | ✓ VERIFIED | Exact shell-free tuple includes `-O1 -mllvm -print-changed -mllvm -print-module-scope`; timeout, byte cap, and no-execution boundary remain substantive and tested. |
| `iris_analyzer/reporting.py` | Deterministic, transactional report artifacts | ✓ VERIFIED | Stable sanitized names, manifest/timeline agreement, staging cleanup, and atomic publication are implemented and tested. |
| `iris_analyzer/cli.py` and `iris_analyzer/__main__.py` | One-command validated orchestration | ✓ VERIFIED | Compiler → parser → cap → report data flow is wired and works through the real module entry point. |
| `examples/loop.c` | Demonstration source | ✓ VERIFIED | Fresh analysis yielded 21 LLVM-classified changed transformations. |
| `README.md` | First-run and artifact guidance | ✓ VERIFIED | Copyable command works and accurately states both LLVM instrumentation prerequisites and standalone snapshot behavior. |
| `tests/test_*.py` | Automated unit and real-toolchain verification | ✓ VERIFIED | 45/45 tests pass; the integration test parses every persisted snapshot with the manifest's resolved compiler. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `parser.py` | `model.py` | `IRSnapshot` construction | ✓ WIRED | `parse_ir_dumps` constructs ordered immutable snapshots. |
| `compiler.py` | Clang | shell-free O1 changed/module-scope argument tuple | ✓ WIRED | Exact production and test tuples agree; fresh manifest records the same tuple used by `/usr/bin/clang`. |
| `compiler.py` | `model.py` | `CompilerOutput` | ✓ WIRED | Returns resolved Clang, exact command tuple, and bounded decoded dump. |
| `cli.py` | compiler/parser/reporting | direct function calls | ✓ WIRED | Real compiler output flows through parsing and cap handling into one transactional report before success output. |
| `manifest.json` | `snapshots/*.ll` | stable relative `file` fields | ✓ WIRED | All 21 fresh links resolved under `snapshots/` and all files parsed as LLVM IR. |
| `README.md` | `examples/loop.c` | copyable module command | ✓ WIRED | README uses the executable `python3 -m iris_analyzer analyze examples/loop.c` spelling. |
| `tests/test_integration.py` | manifest compiler and snapshot entries | same-Clang `-x ir -S -emit-llvm` validation | ✓ WIRED | Lines 82-116 iterate every manifest entry and validate it with `manifest["clang"]`; the test and independent fresh check both pass. |

### Data-Flow Trace (Level 4)

| Artifact | Data | Source | Produces Real Data | Status |
|----------|------|--------|--------------------|--------|
| `cli.py` | validated `CLIConfig` | argparse and filesystem checks | Yes | ✓ FLOWING |
| `compiler.py` | changed-pass module dumps | real `/usr/bin/clang -O1 ... -print-changed ... -print-module-scope` | Yes — 21 changed events in the fresh run | ✓ FLOWING |
| `parser.py` | pass name, scope, complete IR body | LLVM changed-event stream | Yes — identities match raw LLVM and 21/21 bodies parse independently | ✓ FLOWING |
| `reporting.py` | manifest, timeline, numbered snapshots | parsed and capped snapshots | Yes — 21/21 links and timeline entries agree | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full standard-library suite | `python3 -m unittest discover -s tests -v` | 45 passed; local-Clang integration ran | ✓ PASS |
| Python compile check | `python3 -m compileall -q iris_analyzer tests` | Exit 0 | ✓ PASS |
| Fresh documented example | `python3 -m iris_analyzer analyze examples/loop.c --output TMP/report --max-snapshots 25` | Exit 0; 21 retained; manifest, timeline, and 21 snapshots created | ✓ PASS |
| Exact changed-pass attribution | Independently re-ran manifest command and parsed LLVM changed banners | 21 raw events; 21/21 identities matched manifest order | ✓ PASS |
| Standalone snapshot validity | Manifest-resolved Clang parsed every fresh `.ll` via `-x ir -S -emit-llvm` | 21/21 accepted by `/usr/bin/clang` | ✓ PASS |
| Pass-event contamination | Scanned every fresh `.ll` for LLVM `IR Dump`/`IR Pass` banners | 21/21 banner-free | ✓ PASS |
| Timeline/manifest consistency | Compared every manifest identity and link against `timeline.md` | 21/21 matched and resolved | ✓ PASS |
| Configurable cap | Fresh run with `--max-snapshots 2` | 2 retained; `truncated=true` | ✓ PASS |
| Clear invalid-source failure | Analyze a guaranteed-missing `.c` path | Exit 2; concise stderr; no traceback | ✓ PASS |
| Transactional publication | Full-suite failure-injection and non-empty-destination tests | No partial report and no user-file mutation | ✓ PASS |

### Probe Execution

No phase probes were declared and no conventional `scripts/**/tests/probe-*.sh` files exist.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| INPUT-01 | 01-02 | Analyze one existing C source | ✓ SATISFIED | Fresh real module command completed successfully. |
| INPUT-02 | 01-01, 01-02 | Clear invalid-source/toolchain errors | ✓ SATISFIED | Bounded CLI/compiler handling is implemented; fresh missing-source and automated toolchain/compile cases pass. |
| INPUT-03 | 01-01, 01-02 | Explicit Clang override | ✓ SATISFIED | Resolver, CLI flag, and focused override tests are wired. |
| CAPT-01 | 01-01, 01-02, 01-03 | Real LLVM O1 pipeline | ✓ SATISFIED | Fresh manifest records real `/usr/bin/clang -O1`; compiled code is never run. |
| CAPT-02 | 01-01, 01-03 | Ordered pass, scope, and IR body | ✓ SATISFIED | 21/21 manifest identities match raw LLVM order and all bodies are complete modules. |
| CAPT-03 | 01-01, 01-02, 01-03 | Changed consecutive snapshots only | ✓ SATISFIED | LLVM `-print-changed` selects changed events; omitted events are excluded; independent identity comparison is exact. |
| CAPT-04 | 01-01, 01-02 | Positive snapshot cap | ✓ SATISFIED | Positive validation and fresh cap-2 truncation behavior pass. |
| RPRT-01 | 01-02 | JSON manifest | ✓ SATISFIED | Complete stable manifest generated and inspected. |
| RPRT-02 | 01-02 | Markdown timeline | ✓ SATISFIED | Ordered readable timeline agrees with all 21 manifest entries. |
| RPRT-03 | 01-02, 01-03 | Numbered `.ll` snapshots | ✓ SATISFIED | 21/21 fresh numbered files are path-safe, banner-free, and valid standalone LLVM modules. |
| RPRT-04 | 01-02 | Terminal summary | ✓ SATISFIED | Fresh run printed retained count and absolute report path. |
| QUAL-01 | 01-02, 01-03 | README example flow | ✓ SATISFIED | Documented command and artifact contract work against local Clang. |
| QUAL-02 | 01-01, 01-02, 01-03 | Automated full-pipeline verification | ✓ SATISFIED | 45/45 tests pass, including real-Clang same-toolchain artifact validation. |

All 13 Phase 1 requirement IDs appear in plan frontmatter and `.planning/REQUIREMENTS.md`; no Phase 1 requirement is orphaned.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No unresolved `TBD`, `FIXME`, `XXX`, placeholder, stub implementation, third-party dependency, or package install was found in Phase 1 source. | ℹ Info | No completion blocker. The integration test's “clang is not available” text is a legitimate environment skip condition, not a stub. |

### Disconfirmation Pass

- The focused compiler test uses a mocked process, so by itself it proves tuple construction rather than LLVM compatibility; the real integration test and this verifier's independent fresh run close that evidence gap.
- Report unit tests use synthetic IR bodies, so by themselves they do not prove standalone LLVM validity; the real per-artifact validation covers all generated files.
- Unsupported `-print-module-scope` is not given a dedicated custom diagnostic, but it still follows the bounded non-zero compiler-error path with Clang's diagnostic, satisfying INPUT-02 without weakening the user-facing error contract.

### Human Verification Required

None. The Phase 1 goal and the former artifact-validity gap are fully testable through deterministic CLI, filesystem, and real-toolchain checks.

### Gaps Summary

The previous blocker is closed. Adding `-mllvm -print-module-scope` causes LLVM's changed-pass dumps to contain complete modules, and both the automated integration test and an independent fresh verifier run confirm that every generated numbered `.ll` artifact is accepted by the exact resolved Clang. No regressions or remaining Phase 1 gaps were found.

---

_Verified: 2026-09-24T16:14:55Z_
_Verifier: the agent (gsd-verifier)_
