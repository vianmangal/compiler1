<!-- GSD:project-start source:PROJECT.md -->

## Project

**LoopLift**

LoopLift is a deliberately scoped answer to Segfault **P05: Automatic Parallelizing Compiler for GPGPU with Interprocedural Analysis**. It analyzes C loops that call helper functions, follows those calls to determine whether the helpers introduce side effects, and—when the supported loop is safe and worthwhile—emits C with an OpenMP GPU-offload directive plus an explanation of the decision.

The project supports a clear subset of C rather than pretending to parallelize arbitrary programs. That makes the compiler analysis real, the demo understandable, and the implementation achievable for a student hackathon team.

**Core Value:** LoopLift automatically decides whether a supported loop remains safe to parallelize across helper-function calls and explains the evidence behind that decision.

### Constraints

- **Complexity**: Use a narrow, documented C subset and conservative rejection rules.
- **Toolchain**: Use `clang -Xclang -ast-dump=json -fsyntax-only` as the analysis frontend.
- **Stack**: Python 3.10+ standard library for the analyzer and tests.
- **Safety**: Unknown calls, ambiguous pointer writes, global mutation, and unsupported control flow must reject a loop rather than guess.
- **Code generation**: Emit OpenMP `target teams distribute parallel for`, not handwritten CUDA.
- **Delivery**: Phase 1 ends with a usable CLI analyzer, JSON/Markdown reports, examples, and tests.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
