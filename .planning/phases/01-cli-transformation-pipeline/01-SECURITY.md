---
phase: 01-cli-transformation-pipeline
slug: cli-transformation-pipeline
status: verified
register_authored_at_plan_time: true
threats_total: 14
threats_closed: 14
threats_open: 0
asvs_level: 1
block_on: high
audit_date: 2026-09-24
created: 2026-09-24
---

# Phase 1 — Security

> Verification of every mitigation and accepted-risk disposition declared in Plans 01-01, 01-02, and 01-03. Implementation behavior and executable tests are the evidence; plan or summary claims alone are not treated as proof.

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| CLI user -> source/tool/output paths | User-controlled local path and option strings enter validation, compiler selection, and report generation. | Local source paths, compiler override, output directory, snapshot cap |
| IRis -> selected Clang | The analyzer invokes a resolved external compiler without a shell. | Resolved executable and source paths, fixed LLVM flags |
| Clang stderr -> parser/model | Bounded, version-variable compiler output becomes structured snapshots. | LLVM event banners, pass/scope metadata, IR bodies, diagnostics |
| Parsed metadata -> report filesystem | Toolchain-controlled names and IR are persisted into a user-selected report directory. | Sanitized filenames, manifest/timeline metadata, LLVM modules |
| Integration test -> generated snapshots | Each published LLVM artifact is parsed again by the compiler recorded by that run. | Resolved Clang path and generated `.ll` paths |

## Threat Register

| Threat ID | Category | Component | Disposition | Verified control and exact evidence | Status |
|-----------|----------|-----------|-------------|-------------------------------------|--------|
| T-01-01 | Elevation of Privilege | `iris_analyzer/compiler.py` | mitigate | Source and compiler paths are resolved before a fixed argument tuple is built; output targets `os.devnull`; `subprocess.Popen` receives that tuple with `shell=False` and never invokes a produced binary (`compiler.py:45-68`). The exact call is asserted in `tests/test_compiler.py:81-143`. | closed |
| T-01-02 | Spoofing | PATH / `--clang` resolution | mitigate | `shutil.which` resolves the default, command-name, or explicit-path selection; the result must be a regular executable file (`compiler.py:26-39`). The resolved path and exact command are returned (`compiler.py:112-116`) and persisted in the manifest (`reporting.py:127-138`). Resolver edge cases are covered in `tests/test_compiler.py:14-65`. | closed |
| T-01-03 | Denial of Service | Clang execution and dump retention | mitigate | Production capture enforces a 30-second deadline and 16 MiB stream limit, stopping the compiler on breach (`compiler.py:69-92,124-132`). The parser opens only changed `IR Dump After` sections and rejects LLVM events marked unchanged (`parser.py:30-79`); the retained list requires a positive cap and stops at that cap (`parser.py:82-99`). Timeout, output-limit, omitted-event, and cap behavior are executable tests. | closed |
| T-01-04 | Information Disclosure | Compiler diagnostics | accept | Accepted local diagnostic exposure is documented below. Diagnostics are bounded to 4,000 characters (`compiler.py:135-141`), passed only to the local CLI error boundary (`cli.py:121-125`), and the project has no network transport. | closed |
| T-01-05 | Tampering | `iris_analyzer/reporting.py` | mitigate | Untrusted pass names become bounded ASCII components (`reporting.py:17-32`), filenames add stable ordinals and remain under the fixed `snapshots/` directory (`reporting.py:99-115`), and non-empty destinations are rejected before publication (`reporting.py:47-68,78-84`). Traversal, collision, non-empty-destination, and failure-cleanup cases are tested in `tests/test_reporting.py:13-24,60-129,157-193`. | closed |
| T-01-06 | Spoofing | CLI compiler selection and report provenance | mitigate | The CLI delegates both PATH and override selection to `resolve_clang` and passes the resolved path into capture (`cli.py:99-108`). The resulting resolved compiler and exact command are written to `manifest.json` (`reporting.py:127-138`). Both resolution routes and CLI override delegation are tested (`tests/test_compiler.py:21-45`; `tests/test_cli.py:141-150`). | closed |
| T-01-07 | Denial of Service | CLI retention and report persistence | mitigate | `--max-snapshots` accepts only positive integers (`cli.py:25-32,59-65`), is propagated to `retain_changed` (`cli.py:99-119`), and the report writer receives only the returned bounded snapshot list. Cap propagation and exactly one persisted artifact at cap 1 are asserted in `tests/test_cli.py:119-139`. | closed |
| T-01-08 | Repudiation | Report provenance | mitigate | The deterministic manifest records source, resolved Clang, exact command, optimization level, captured/retained counts, configured cap, truncation, and per-snapshot identity/path (`reporting.py:103-144`). The complete schema and values are asserted in `tests/test_reporting.py:60-122`. | closed |
| T-01-09 | Information Disclosure | User-facing errors | accept | Accepted local error disclosure is documented below. Expected errors are converted to one concise stderr message and exit code 2 (`cli.py:121-125`); compiler diagnostics are bounded (`compiler.py:135-141`); tests verify expected failures contain no traceback (`tests/test_cli.py:171-232`). | closed |
| T-01-10 | Tampering | Clang command construction | mitigate | Production constructs the exact ordered `-O1 -S -emit-llvm -mllvm -print-changed -mllvm -print-module-scope SOURCE -o DEVNULL` tuple and passes it with `shell=False` (`compiler.py:45-68`). The complete tuple and subprocess contract are asserted in `tests/test_compiler.py:81-95,129-143`. | closed |
| T-01-11 | Spoofing | Snapshot compatibility validation | mitigate | Every manifest snapshot is validated with `manifest["clang"]`, the compiler recorded by the same run, rather than a later PATH lookup (`tests/test_integration.py:82-116`). The passing real-Clang integration test exercises the full set. | closed |
| T-01-12 | Denial of Service | Capture and snapshot validation | mitigate | Production retains its 30-second and 16 MiB bounds (`compiler.py:69-92`) and report count cap (`parser.py:82-99`). Each real-Clang artifact validation has a 30-second timeout and bounded diagnostic text (`tests/test_integration.py:94-116`). | closed |
| T-01-13 | Elevation of Privilege | Snapshot validation subprocess | mitigate | Validation uses a fixed argument list with the recorded compiler, `-x ir -S -emit-llvm`, and `-o os.devnull`; it captures output, sets a timeout, does not use a shell, and never links or runs generated code (`tests/test_integration.py:94-109`). | closed |
| T-01-SC | Tampering | Package-manager installs | accept | Accepted dependency-policy risk is documented below. No Python/package-manager dependency metadata is present, no install step appears in the reviewed implementation, and all production/test imports are Python standard library or local `iris_analyzer` modules. The full suite runs without third-party packages. | closed |

*Status: open · closed. Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party).*

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-01-04 | This is a local educational CLI operating on a user-selected source file. A bounded compiler diagnostic is necessary to explain compilation/toolchain failures, remains on the local machine, and is not transmitted. | Plan 01-01 plan-time disposition | 2026-09-24 |
| AR-02 | T-01-09 | Concise local source/compiler/report errors are necessary for usable failure handling. Expected exceptions are rendered without tracebacks, diagnostics are bounded, and no network transport exists. | Plan 01-02 plan-time disposition | 2026-09-24 |
| AR-03 | T-01-SC | Phase 1 deliberately has no package-manager install or third-party runtime/test dependency. The residual supply-chain decision is to stop and perform a package-legitimacy review before any future dependency is introduced. | Plans 01-01, 01-02, and 01-03 plan-time disposition | 2026-09-24 |

## Summary Threat Flags

No `## Threat Flags` section or executor-raised threat flag appears in the three plan summaries. There are no unregistered flags.

## Verification Run

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` — 45 tests passed, including the real local-Clang integration test.
- No `requirements*.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile*`, `package*.json`, or `Cargo.toml` exists in the repository.
- Import inspection found only Python standard-library modules and local package imports.

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 14 | 14 | 0 | Codex security auditor |

## Sign-Off

- [x] All threats have a disposition (`mitigate` or `accept`; no transfers declared)
- [x] Every mitigation is evidenced in implementation and/or executable tests
- [x] Accepted risks are documented in the Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
