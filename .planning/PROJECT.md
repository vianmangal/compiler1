# IRis

## What This Is

IRis is a small explainable-compiler tool for the Segfault hackathon's **P01: LLVM Pass Transformation Analyzer** problem statement. It accepts a C program, asks Clang to expose the LLVM optimization pipeline, and turns the resulting IR snapshots into a readable transformation timeline for students, faculty, and developers learning why optimized code changes.

## Core Value

A user can run one command and clearly see which LLVM passes changed their program's IR.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Analyze a local C source file using the installed Clang toolchain.
- [ ] Capture and retain the LLVM IR snapshots that actually change during optimization.
- [ ] Produce a deterministic report that a user can inspect without knowing LLVM internals.
- [ ] Explain common transformations with simple descriptions and change metrics.
- [ ] Offer a lightweight visual timeline suitable for a short hackathon demo.

### Out of Scope

- AI/ML-based optimization prediction — adds data, training, and evaluation complexity without helping the core demo.
- GPU compilation, OpenCL debugging, or automatic parallelization — requires specialized hardware and substantially more compiler infrastructure.
- A custom compiler, optimizer, or LLVM pass — IRis observes LLVM; it does not replace LLVM.
- Production-scale or untrusted-code sandboxing — v1 is a local educational tool for small examples.
- Supporting languages other than C — one dependable input path is enough for the hackathon MVP.

## Context

- The project is for Segfault, a compiler-focused hackathon.
- The submitted problem list includes LLVM pass analysis, AI compiler stacks, optimization cost models, GPU profitability, automatic GPGPU parallelization, and OpenCL debugging.
- P01 is selected because it has the smallest dependency surface, produces a visual and technically authentic demo, and can be explained to faculty without requiring GPU or ML expertise.
- Apple Clang 21 is already present locally and supports LLVM pass-manager diagnostics and IR dumps.
- The workspace is a new Git repository with no existing application constraints.

## Constraints

- **Complexity**: Keep the architecture understandable to a student team — avoid services, databases, accounts, and distributed components.
- **Toolchain**: Use the installed Clang first — do not require Homebrew LLVM for the MVP.
- **Stack**: Python standard library for Phase 1 — setup should remain small and offline-friendly.
- **Scope**: Optimize for a convincing small-program demo, not exhaustive LLVM coverage.
- **Delivery**: Phase 1 must be a working vertical CLI slice with automated tests.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Choose P01: LLVM Pass Transformation Analyzer | Lowest implementation risk while remaining a real compiler project | — Pending |
| Name the project IRis | Short, memorable, and communicates making IR visible | — Pending |
| Use Clang's pass dump output rather than requiring `opt` | Works with the toolchain already installed on macOS | — Pending |
| Build a CLI before a browser UI | Proves the compiler pipeline early and keeps Phase 1 small | — Pending |
| Compare consecutive snapshots within the same IR scope | Avoids claiming a change when dumps refer to different functions/modules | — Pending |

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
*Last updated: 2026-09-10 after initialization*
