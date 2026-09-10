# Product Requirements Document: IRis

**Hackathon:** Segfault  
**Selected statement:** P01 — LLVM Pass Transformation Analyzer  
**Theme:** Explainable compilers  
**Status:** Approved for implementation  
**Date:** 2026-09-10

## 1. Why This Problem

IRis uses P01 because it is the clearest balance of technical credibility, low complexity, and demo value.

| Candidate | Complexity | Extra infrastructure | Demo clarity | Decision |
|-----------|------------|----------------------|--------------|----------|
| P01 LLVM pass analyzer | Low–medium | Clang only | Very high | **Selected** |
| P02 AI compiler explorer | High | Multiple IR frameworks | Medium | Too broad |
| P03 optimization cost model | High | Benchmarks and ML/data | Medium | Too research-heavy |
| P04 GPU profitability predictor | High | GPU and performance dataset | Medium | Hardware-dependent |
| P05 automatic GPGPU compiler | Very high | Compiler analysis and GPU backend | Low for available time | Too complex |
| P06 OpenCL debugger | Very high | GPU ISA/debugger integration | High if complete | Too risky |

P01 also has a simple story for judges: “Here is the C code, here is LLVM IR before optimization, and here are only the passes that changed it.”

## 2. Product Summary

IRis is a local educational analyzer that turns verbose LLVM pass dumps into a compact timeline. A user points it at a small C file; IRis invokes Clang, extracts pass snapshots, removes unchanged repetitions, and creates a report containing the transformation order and saved IR.

## 3. Users

- Students learning compiler optimization.
- Faculty reviewing a technically sound but easy-to-follow project.
- Hackathon judges who need to understand the value in a short demo.
- Developers debugging why an optimization pipeline changed a small function.

## 4. User Story

As a student, I want to run an analyzer on a C program and see the LLVM passes that actually changed its IR, so I can understand optimization without reading a huge compiler debug log.

## 5. Primary Flow

1. The user selects a `.c` source file.
2. The user runs `iris analyze examples/loop.c`.
3. IRis checks Clang availability and compiles the source through an optimization pipeline.
4. IRis parses pass snapshots and keeps meaningful changes.
5. IRis writes a report directory with a manifest, timeline, and `.ll` snapshots.
6. The terminal prints a short summary and where to inspect the report.

## 6. Functional Requirements

### Phase 1 — Working CLI MVP

- Accept one existing C source path and an optional report directory.
- Discover a compatible `clang` executable or accept an explicit override.
- Run Clang at `-O1` with LLVM pass-manager IR dumps enabled.
- Parse pass name, IR scope, order, and IR body from the compiler output.
- Suppress consecutive unchanged dumps for the same scope.
- Save a JSON manifest, Markdown timeline, and numbered LLVM IR snapshots.
- Return clear non-zero errors for invalid input, missing Clang, and compilation failure.
- Include a small example and automated unit/integration tests.

### Phase 2 — Explanations and Comparisons

- Show added/removed line counts between adjacent comparable snapshots.
- Attach plain-English descriptions to common passes.
- Generate unified diffs for selected transformations.
- Allow basic filtering by function or pass name.

### Phase 3 — Visual Demo

- Provide a lightweight local web page showing the transformation timeline.
- Show side-by-side IR and highlighted changes for a selected pass.
- Export or open an existing CLI report without rerunning Clang.

## 7. Non-Functional Requirements

- Phase 1 uses only Python's standard library at runtime.
- A normal small C example should finish in under 10 seconds on the development machine.
- Reports are deterministic apart from toolchain-provided target metadata.
- Compiler commands are executed without a shell and never interpolate source text into a command string.
- The codebase remains small enough to explain module-by-module during evaluation.

## 8. Out of Scope

- Running submitted programs or evaluating their runtime behavior.
- Compiling untrusted source on a public server.
- Reimplementing LLVM optimization passes.
- ML-generated explanations or optimization recommendations.
- GPU, CUDA, OpenCL, MLIR, or multi-language input in v1.
- Authentication, cloud storage, collaboration, or project accounts.

## 9. Success Measures

- The provided example produces at least two retained transformation snapshots on the local Clang toolchain.
- A first-time user can generate and find the report from the README instructions.
- Automated tests cover parsing, unchanged-snapshot filtering, report writing, CLI validation, and one real Clang smoke path when available.
- The demo can be explained in under three minutes: input → LLVM pipeline → transformation timeline.

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLVM dump formatting differs between Clang versions | Keep parsing isolated, tolerate banner variants, and test against fixtures plus local Clang |
| Pass output is extremely large | Retain only changed snapshots and support a maximum snapshot count |
| Function and module dumps are compared incorrectly | Track previous IR independently for each scope |
| A judge lacks Clang | Document the dependency and include a pre-generated example report in a later phase |
| UI consumes hackathon time | Finish and verify the CLI before beginning the web viewer |

## 11. Definition of Done for Phase 1

- `python -m iris_analyzer analyze examples/loop.c` succeeds with local Clang.
- The command creates `manifest.json`, `timeline.md`, and at least two `.ll` snapshot files.
- Invalid source and compiler failures have readable messages and non-zero exit codes.
- The test suite passes from a clean checkout.
- README documents installation, command usage, output structure, and the project boundary.
