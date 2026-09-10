# LoopLift

## What This Is

LoopLift is a deliberately scoped answer to Segfault **P05: Automatic Parallelizing Compiler for GPGPU with Interprocedural Analysis**. It analyzes C loops that call helper functions, follows those calls to determine whether the helpers introduce side effects, and—when the supported loop is safe and worthwhile—emits C with an OpenMP GPU-offload directive plus an explanation of the decision.

The project supports a clear subset of C rather than pretending to parallelize arbitrary programs. That makes the compiler analysis real, the demo understandable, and the implementation achievable for a student hackathon team.

## Core Value

LoopLift automatically decides whether a supported loop remains safe to parallelize across helper-function calls and explains the evidence behind that decision.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Parse real Clang AST output for local C source files.
- [ ] Discover loops, functions, call relationships, and cross-function side effects.
- [ ] Conservatively label supported loops safe or unsafe with concrete reasons.
- [ ] Transform safe loops into OpenMP target-offload candidates without changing rejected loops.
- [ ] Avoid offloading obviously unprofitable loops using a small deterministic heuristic.
- [ ] Produce an explainable report and validation-oriented hackathon demo.

### Out of Scope

- Full ISO C support — the MVP handles a documented canonical-loop subset.
- CUDA kernel generation or a custom GPU backend — OpenMP target directives keep code generation small and portable.
- Advanced pointer/alias analysis — ambiguous memory access is rejected conservatively.
- ML-based profitability prediction — would require a trustworthy dataset and distract from compiler analysis.
- Guaranteed GPU execution on the development Mac — generated offload code can be inspected and compile-checked where a compatible OpenMP toolchain is available.
- Whole-program optimization across separate translation units — v1 analyzes one C source file.

## Context

- The project is for Segfault, a compiler-focused hackathon.
- P05 is more ambitious and distinctive than the previously considered P01 pass viewer.
- The user wants a project that is impressive but still straightforward enough to explain to faculty.
- Apple Clang 21 is installed and can emit its AST as JSON, allowing real compiler parsing without linking LLVM libraries.
- Phase 1 intentionally proves the hardest claim first: interprocedural safety analysis. Automatic source transformation follows only after the analyzer is trustworthy.

## Constraints

- **Complexity**: Use a narrow, documented C subset and conservative rejection rules.
- **Toolchain**: Use `clang -Xclang -ast-dump=json -fsyntax-only` as the analysis frontend.
- **Stack**: Python 3.10+ standard library for the analyzer and tests.
- **Safety**: Unknown calls, ambiguous pointer writes, global mutation, and unsupported control flow must reject a loop rather than guess.
- **Code generation**: Emit OpenMP `target teams distribute parallel for`, not handwritten CUDA.
- **Delivery**: Phase 1 ends with a usable CLI analyzer, JSON/Markdown reports, examples, and tests.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Select P05 with a supported-subset scope | More hackathon depth than P01 without attempting an industrial compiler | — Pending |
| Name the project LoopLift | Communicates lifting serial loops into parallel execution | — Pending |
| Use Clang JSON AST | Real compiler structure is more defensible than regex parsing and is available locally | — Pending |
| Make analysis conservative | False negatives are acceptable; unsafe automatic parallelization is not | — Pending |
| Summarize helper effects transitively | Demonstrates genuine interprocedural reasoning across call chains | — Pending |
| Generate OpenMP target directives | Represents GPGPU offload with much less backend complexity than CUDA generation | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-10 after the P05 scope pivot*
