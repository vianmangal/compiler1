# Phase 1: CLI Transformation Pipeline - Context

**Gathered:** 2026-09-10
**Status:** Ready for planning
**Source:** PRD Express Path (`docs/PRD.md`)

<domain>
## Phase Boundary

Deliver one local command that validates a C source file, invokes the installed Clang `-O1` LLVM optimization pipeline with pass dumps, retains meaningful changed snapshots, and writes an inspectable report. Browser UI, pass explanations, diffs, GPU support, and AI recommendations remain outside this phase.

</domain>

<decisions>
## Implementation Decisions

### Input and toolchain
- **D-01 (locked):** Accept exactly one existing `.c` source path per analysis.
- **D-02 (locked):** Discover `clang` from `PATH` by default and support an explicit `--clang` executable override.
- **D-03 (locked):** Fail with readable non-zero CLI errors for an invalid path, wrong extension, missing compiler, or compilation failure.

### Transformation capture
- **D-04 (locked):** Use Clang's real `-O1` pipeline with `-mllvm -print-after-all`; do not simulate compiler passes.
- **D-05 (locked):** Parse ordered pass name, IR scope, and IR body from `IR Dump After` sections.
- **D-06 (locked):** Compare consecutive snapshots independently within each IR scope and retain only changed IR.
- **D-07 (locked):** Bound retained output through a positive `--max-snapshots` option.

### Reporting
- **D-08 (locked):** Produce `manifest.json`, `timeline.md`, and numbered `.ll` files under a user-selected or default report directory.
- **D-09 (locked):** Print the retained count and report location after success.
- **D-10 (locked):** Use stable, sanitized snapshot filenames and structured JSON fields suitable for a later browser viewer.

### Quality and safety
- **D-11 (locked):** Use Python 3.10+ and only the standard library at runtime in Phase 1.
- **D-12 (locked):** Execute Clang with an argument list and `shell=False`; do not execute the compiled program.
- **D-13 (locked):** Include unit tests, a conditional real-Clang smoke test, an example C program, and README instructions.

### the agent's Discretion
- Exact Python package/module layout.
- Dataclass field names beyond the report contract.
- Parser regular-expression structure and internal exception hierarchy.
- Default output directory naming and Markdown presentation details.
- Whether the test suite uses `unittest.mock` or small fake executables for failure cases.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and scope
- `docs/PRD.md` — selected problem, user flow, requirements, risks, and Phase 1 definition of done.
- `docs/IMPLEMENTATION_PLAN.md` — intended Phase 1 architecture, work items, technical choices, and verification strategy.
- `.planning/REQUIREMENTS.md` — canonical v1 requirement IDs and traceability.
- `.planning/ROADMAP.md` — phase boundary and observable success criteria.

</canonical_refs>

<specifics>
## Specific Ideas

- Expected demo command: `python -m iris_analyzer analyze examples/loop.c`.
- Expected artifact names: `manifest.json`, `timeline.md`, and `snapshots/NNN-pass-name.ll`.
- The development machine currently provides Apple Clang 21, and a probe confirmed both `-Xclang -fdebug-pass-manager` and `-mllvm -print-after-all` are available.

</specifics>

<deferred>
## Deferred Ideas

- Phase 2: pass descriptions, line metrics, unified diffs, and filters.
- Phase 3: a local browser timeline and side-by-side IR comparison.
- Out of scope: AI recommendations, GPU/OpenCL flows, custom passes, multiple source languages, and a public compilation service.

</deferred>

---
*Phase: 01-cli-transformation-pipeline*
*Context gathered: 2026-09-10 via PRD Express Path*
