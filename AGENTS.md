<!-- GSD:project-start source:PROJECT.md -->

## Project

**IRis**

IRis is a small explainable-compiler tool for the Segfault hackathon's **P01: LLVM Pass Transformation Analyzer** problem statement. It accepts a C program, asks Clang to expose the LLVM optimization pipeline, and turns the resulting IR snapshots into a readable transformation timeline for students, faculty, and developers learning why optimized code changes.

**Core Value:** A user can run one command and clearly see which LLVM passes changed their program's IR.

### Constraints

- **Complexity**: Keep the architecture understandable to a student team — avoid services, databases, accounts, and distributed components.
- **Toolchain**: Use the installed Clang first — do not require Homebrew LLVM for the MVP.
- **Stack**: Python standard library for Phase 1 — setup should remain small and offline-friendly.
- **Scope**: Optimize for a convincing small-program demo, not exhaustive LLVM coverage.
- **Delivery**: Phase 1 must be a working vertical CLI slice with automated tests.

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
