# Product Requirements Document: LoopLift

**Hackathon:** Segfault  
**Selected statement:** P05 — Automatic Parallelizing Compiler for GPGPU with Interprocedural Analysis  
**Project scope:** P05-lite: conservative source-to-source compiler for a documented C subset  
**Status:** Approved for implementation  
**Date:** 2026-09-10

## 1. Why P05

P01 was feasible but risked looking like a visualization wrapper around compiler output. P05 gives the project a stronger compiler contribution: LoopLift must reason about loops, function calls, side effects, data independence, and code transformation.

The full research problem is too large for a hackathon, so LoopLift makes the supported language boundary explicit. It only transforms canonical loops for which it can establish safety; every other loop is preserved and receives a rejection explanation. This is both achievable and technically honest.

## 2. Product Summary

LoopLift accepts one C source file, invokes Clang to obtain a JSON AST, and builds a small interprocedural program model. It discovers `for` loops, follows helper-function calls, summarizes observable side effects, and classifies each loop as a parallelization candidate or a conservative rejection. Later phases add an OpenMP GPU-offload rewrite, a profitability gate, and a polished explainability report.

## 3. Target Users

- Students learning compiler dependence and side-effect analysis.
- Faculty evaluating a clear compiler pipeline with inspectable rules.
- Hackathon judges looking for a technically meaningful transformation demo.
- Developers experimenting with simple data-parallel C kernels.

## 4. Main User Story

As a C developer, I want the compiler to inspect loops that call helper functions and tell me whether they can be GPU-parallelized, so I do not have to reason manually about every transitive side effect.

## 5. Supported Input Subset

The first release targets single-file C programs containing canonical `for` loops such as `for (int i = 0; i < n; i++)` and helper functions defined in the same file.

The safety analyzer may approve a loop when:

- Its body has no `break`, `goto`, or `return`.
- Scalar state shared between iterations is not mutated.
- Array writes are indexed by the loop induction variable.
- Called helpers are defined locally and their transitive callees are side-effect safe.
- Helpers do not mutate globals, perform ambiguous pointer writes, or call unknown impure functions.

Anything outside this subset is rejected with one or more reason codes; it is never silently transformed.

## 6. Product Flow

1. User runs `looplift analyze examples/safe_map.c`.
2. LoopLift validates the source and Clang executable.
3. Clang produces a JSON AST without running the program.
4. LoopLift builds function summaries and a call graph.
5. Each discovered loop is evaluated using local and transitive evidence.
6. A terminal summary plus JSON and Markdown reports identify safe and rejected loops.
7. In Phase 2, `looplift transform` inserts an OpenMP target directive only for approved loops.

## 7. Functional Requirements

### Phase 1 — Interprocedural Safety Analyzer

- Accept one existing `.c` source file and an optional Clang override.
- Parse real Clang JSON AST output without third-party parser dependencies.
- Discover defined functions, their direct callees, and all `for` loops.
- Summarize global mutation, pointer-parameter mutation risk, unknown/external calls, and unsupported control flow.
- Propagate unsafety through the local call graph, including recursion/cycles.
- Recognize a narrow canonical induction-variable pattern.
- Classify each loop as `safe`, `unsafe`, or `unsupported` with stable reason codes and human-readable evidence.
- Emit `analysis.json`, `report.md`, and a concise terminal summary.
- Provide safe, unsafe, and transitive-call examples plus automated tests.

### Phase 2 — Automatic GPGPU-Oriented Transformation

- Add `looplift transform` for approved loops.
- Insert `#pragma omp target teams distribute parallel for` immediately before each approved loop.
- Preserve all other source text and never modify rejected loops.
- Produce a transformed `.c` file and a transformation manifest.
- Support dry-run output for demonstration and review.

### Phase 3 — Profitability, Validation, and Demo

- Reject clearly tiny/unknown-trip loops unless the user explicitly overrides the profitability gate.
- Estimate loop work using simple operation and call counts rather than ML.
- Compile-check transformed output when a compatible OpenMP toolchain is available.
- Produce a self-contained HTML explanation view from an existing analysis report.
- Include a pre-generated example so the core demo remains viewable without a GPU.

## 8. Non-Functional Requirements

- Python standard library only at runtime.
- Analysis of supplied examples completes in under 10 seconds on the development machine.
- Subprocesses are invoked as argument arrays without a shell.
- Results are deterministic for a fixed source file and Clang version.
- Every non-approved loop has at least one explicit reason.
- The implementation is modular enough to explain as frontend → model → analysis → report → rewrite.

## 9. Non-Goals

- Proving safety for arbitrary pointer arithmetic, macros, function pointers, or complex aliasing.
- Generating CUDA, HIP, or SPIR-V directly.
- Training a performance model.
- Running untrusted code in a public service.
- Claiming speedup without suitable GPU hardware and a reproducible benchmark.
- Replacing production LLVM dependence analysis.

## 10. Success Metrics

- Phase 1 identifies at least one safe loop and three different rejection cases in the included examples.
- A transitive unsafe helper (`loop → helper A → helper B → global write`) causes the loop to be rejected with a visible call-chain explanation.
- Phase 2 transforms only the approved example and leaves rejected examples unchanged.
- The full project can be demonstrated in under four minutes: analyze → explain → transform → inspect.

## 11. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Clang AST shape varies | Isolate AST traversal, avoid depending on irrelevant nodes, and maintain fixture tests |
| Analysis overclaims safety | Default to rejection for unknown calls, cycles, pointers, and unsupported constructs |
| Source rewriting corrupts formatting | Phase 2 inserts text only at Clang-provided source offsets and compile-checks output |
| GPGPU claim cannot be demonstrated on macOS | Generate standard OpenMP target code and include inspectable artifacts; validate on a compatible environment when available |
| Scope expands toward a full compiler | Keep the supported subset and reason-code list explicit in docs and tests |

## 12. Phase 1 Definition of Done

- `python -m looplift analyze examples/safe_map.c` succeeds with local Clang.
- Output lists functions, call edges, loops, classifications, and reason evidence.
- Safe, direct-unsafe, and transitively unsafe examples behave as documented.
- `analysis.json` and `report.md` are generated.
- Missing source, invalid C, and missing Clang return readable non-zero errors.
- Automated tests pass using both AST fixtures and a conditional real-Clang integration test.
