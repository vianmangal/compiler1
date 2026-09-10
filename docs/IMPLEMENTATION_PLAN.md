# LoopLift Implementation Plan

## Architecture

```text
C source
  ↓
Clang JSON AST frontend
  ↓
Program model ── functions, calls, loops, source locations
  ↓
Interprocedural summary engine
  ├── global writes
  ├── pointer mutation risk
  ├── external/unknown calls
  └── transitive callee safety
  ↓
Loop safety classifier
  ├── safe
  ├── unsafe
  └── unsupported
  ↓
JSON / Markdown report
  ↓ Phase 2
OpenMP target source rewriter
```

## Phase 1 — Interprocedural Safety Analyzer

**Goal:** Prove the hard compiler-analysis claim using a real Clang AST and explainable conservative decisions.

### Deliverables

1. Python package and `looplift analyze` CLI.
2. Safe Clang discovery and JSON AST invocation.
3. AST traversal helpers that tolerate absent optional fields.
4. Program model for functions, calls, loops, and source locations.
5. Direct function-effect summaries.
6. Call-graph propagation for transitive unsafety and recursion.
7. Canonical-loop recognition and loop safety classification.
8. Stable reason codes with short explanations.
9. JSON and Markdown reports.
10. Safe/unsafe examples, README, unit tests, and real-Clang smoke test.

### Planned modules

| Module | Responsibility |
|--------|----------------|
| `looplift/clang_frontend.py` | Validate source, find Clang, invoke AST dump, decode errors |
| `looplift/model.py` | Dataclasses/enums for program facts and decisions |
| `looplift/ast_utils.py` | Generic traversal, node lookup, names, ranges, offsets |
| `looplift/analyzer.py` | Function discovery, direct effects, calls, loop facts |
| `looplift/interprocedural.py` | Transitive safety propagation and call-chain evidence |
| `looplift/classifier.py` | Conservative loop decision rules |
| `looplift/report.py` | JSON and Markdown artifacts |
| `looplift/cli.py` | User arguments, orchestration, terminal output, exit codes |

### Phase 1 acceptance checks

- A safe `out[i] = square(in[i])` loop is approved when `square` only computes from scalar inputs.
- A loop calling a helper that writes a global is rejected.
- A loop calling a helper that calls another global-writing helper is rejected with the transitive chain.
- A loop with unsupported control flow is not approved.
- Reports contain no loop without a decision and reason/evidence.

## Phase 2 — OpenMP Target Rewriter

**Goal:** Turn approved analysis results into an automatic, reviewable GPGPU-oriented source transformation.

### Deliverables

- `looplift transform` command.
- Offset-based insertion of `#pragma omp target teams distribute parallel for`.
- No-op behavior for rejected/unsupported loops.
- Transformed source and manifest.
- Compile/syntax check and rewrite tests.

## Phase 3 — Profitability, Validation, and Demo

**Goal:** Avoid silly offloads and present LoopLift as a polished, evidence-driven hackathon project.

### Deliverables

- Deterministic trip-count/work heuristic with override flag.
- Optional OpenMP compile-check adapter.
- HTML report generated from `analysis.json`.
- Pre-generated examples and a four-minute demo script.

## Technical Choices

| Area | Choice | Reason |
|------|--------|--------|
| Language | Python 3.10+ | Fast implementation and faculty-readable code |
| Frontend | Clang JSON AST | Real compiler structure without LLVM library bindings |
| Parallel target | OpenMP target directive | Standard source-level GPU offload with minimal backend work |
| Policy | Conservative allowlist | Safer and more defensible than guessing about aliases/effects |
| Storage | JSON + Markdown files | Transparent, portable, no database |
| Tests | `unittest` | No third-party test dependency |

## Verification Strategy

- Hand-sized AST fixtures for deterministic unit tests.
- Unit tests for traversal, summaries, cycles, transitive call-chain evidence, and decision rules.
- Temporary-directory tests for JSON/Markdown report output.
- CLI error-path tests.
- Conditional integration tests against discovered local Clang.
- Phase 2 golden-file tests to prove rejected loops are byte-for-byte unchanged.

## Complexity Guardrails

LoopLift will not attempt general alias analysis, polyhedral optimization, multi-file linking, CUDA code generation, or learned profitability. A conservative rejection is an expected and explainable result, not a failure.
