# Phase 1: Interprocedural Safety Analyzer - Context

**Gathered:** 2026-09-10
**Status:** Ready for planning
**Source:** PRD Express Path (`docs/PRD.md`)

<domain>
## Phase Boundary

Deliver a command-line analyzer for one C source file. It must use Clang's JSON AST to discover functions, calls, and `for` loops; compute conservative direct and transitive side-effect evidence; classify every discovered loop; and emit terminal, JSON, and Markdown results. Source transformation, profitability scoring, HTML UI, and GPU execution belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### Compiler frontend

- **D-01:** Invoke Clang as an argument-array subprocess with `-Xclang -ast-dump=json -fsyntax-only`; never execute the user's compiled program.
- **D-02:** Accept exactly one existing `.c` file and allow `--clang PATH` as an override.
- **D-03:** Keep AST access defensive: missing optional keys produce conservative results or readable errors, not tracebacks.

### Supported analysis

- **D-04:** Approve only a documented canonical `for` loop whose induction variable can be recognized from its initializer, condition, and increment.
- **D-05:** Treat global mutation, ambiguous pointer-parameter mutation, unknown/external calls, unsupported loop control flow, and recursive call cycles as rejection evidence.
- **D-06:** Compute helper safety transitively across locally defined call edges and retain at least one call chain explaining propagated unsafety.
- **D-07:** Array writes may be considered candidate-safe only when indexed by the recognized induction variable; ambiguous scalar/shared writes are rejected.

### Results and UX

- **D-08:** Every loop receives exactly one status: `safe`, `unsafe`, or `unsupported`.
- **D-09:** Every non-safe result contains stable machine-readable reason codes and human-readable evidence.
- **D-10:** Write `analysis.json` and `report.md` to an explicit or deterministic output directory, and print a compact terminal summary.
- **D-11:** Include safe, direct-unsafe, transitively unsafe, and recursive examples plus standard-library automated tests.

### the agent's Discretion

- Exact package layout, internal dataclass fields, and traversal helper names.
- Exact stable reason-code spelling, provided tests and docs treat it as public output.
- Whether direct and transitive summaries are stored separately or combined in the serialized report.
- Report formatting details that do not hide required evidence.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and scope

- `docs/PRD.md` — Product boundary, supported C subset, requirements, risks, and Phase 1 Definition of Done.
- `docs/IMPLEMENTATION_PLAN.md` — Architecture, planned modules, examples, and verification strategy.

### Project tracking

- `.planning/PROJECT.md` — Core value, constraints, and key decisions.
- `.planning/REQUIREMENTS.md` — Exact Phase 1 requirement IDs and traceability.
- `.planning/ROADMAP.md` — Phase boundary and observable success criteria.

</canonical_refs>

<specifics>
## Specific Ideas

- The headline safe example is `out[i] = square(in[i])` with a pure scalar helper.
- The headline interprocedural rejection is `loop → helper A → helper B → global write`.
- Explain conservative rejection as a correctness feature rather than a limitation hidden from users.
- Use real Clang AST output so the project can credibly claim compiler-based analysis rather than text matching.

</specifics>

<deferred>
## Deferred Ideas

- OpenMP target pragma insertion is Phase 2.
- Trip-count/work profitability heuristics, compile-checking, and HTML demonstration are Phase 3.
- Multi-file analysis, advanced alias analysis, and CUDA/HIP generation remain v2 or out of scope.

</deferred>

---
*Phase: 01-interprocedural-safety-analyzer*
*Context gathered: 2026-09-10 via PRD Express Path*
