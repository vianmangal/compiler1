# Roadmap: LoopLift

## Overview

LoopLift proves the most important compiler claim first: safe interprocedural reasoning across helper calls. Once that evidence is trustworthy, the project adds a narrow OpenMP GPU-offload rewrite and then a simple profitability/validation/demo layer.

## Phases

- [ ] **Phase 1: Interprocedural Safety Analyzer** - Parse Clang ASTs, build call/effect summaries, and explain which loops are safe candidates.
- [ ] **Phase 2: OpenMP Target Rewriter** - Automatically insert GPU-offload directives for approved loops only.
- [ ] **Phase 3: Profitability, Validation, and Demo** - Avoid poor offloads, validate generated code where possible, and present the evidence clearly.

## Phase Details

### Phase 1: Interprocedural Safety Analyzer
**Goal:** Users can analyze a C file and receive a conservative, explainable parallelization decision for every discovered loop, including hazards reached through helper-function calls.
**Mode:** mvp
**Depends on:** Nothing (first phase)
**Requirements:** INPT-01, INPT-02, INPT-03, INPT-04, ANLY-01, ANLY-02, ANLY-03, ANLY-04, ANLY-05, CLSF-01, CLSF-02, CLSF-03, RPRT-01, RPRT-02, QUAL-01
**Success Criteria** (what must be TRUE):
1. User can run one command on a valid C file and LoopLift obtains a real JSON AST from discovered or explicitly selected Clang without executing the program.
2. Output identifies functions, direct call edges, each `for` loop's function/line, and direct effect facts.
3. A canonical map-style loop calling a pure local helper is approved, while global mutation, ambiguous pointer effects, unknown calls, unsupported control flow, and recursive cycles are conservatively rejected.
4. Unsafety propagates through multiple local helper calls and the report shows the relevant call chain and stable reason code.
5. JSON, Markdown, terminal output, examples, and automated tests collectively demonstrate every Phase 1 requirement.
**Plans:**
- Wave 1: `01-01` — package, model, AST utilities, and Clang frontend
- Wave 2 *(blocked on Wave 1)*: `01-02` — direct/transitive analysis and loop classification
- Wave 3 *(blocked on Wave 2)*: `01-03` — reports, CLI, examples, documentation, and integration tests

### Phase 2: OpenMP Target Rewriter
**Goal:** Users can automatically produce reviewable C source with OpenMP GPU-offload directives on approved loops and no changes to rejected loops.
**Mode:** mvp
**Depends on:** Phase 1
**Requirements:** TRNS-01, TRNS-02, TRNS-03, TRNS-04
**Success Criteria** (what must be TRUE):
1. `looplift transform` inserts `#pragma omp target teams distribute parallel for` immediately before every approved loop selected from Phase 1 analysis.
2. Original source remains unchanged and rejected/unsupported loops are byte-for-byte unmodified in generated output.
3. User can preview the planned edits and inspect a transformation manifest before using the output.
**Plans:** TBD

### Phase 3: Profitability, Validation, and Demo
**Goal:** Users can avoid obviously poor offloads, validate generated source when supported, and present LoopLift's decisions without requiring GPU hardware.
**Mode:** mvp
**Depends on:** Phase 2
**Requirements:** PROF-01, PROF-02, VALD-01, DEMO-01, DEMO-02
**Success Criteria** (what must be TRUE):
1. Every approved safety candidate receives a deterministic profitability result and users can override a rejection for experimentation.
2. LoopLift compile-checks transformed source when a compatible OpenMP toolchain is configured and reports unavailable toolchains honestly.
3. A self-contained HTML report and pre-generated example demonstrate analysis evidence and transformation output without GPU hardware.
**Plans:** TBD
**UI hint:** yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Interprocedural Safety Analyzer | 0/3 | Planned | - |
| 2. OpenMP Target Rewriter | 0/TBD | Not started | - |
| 3. Profitability, Validation, and Demo | 0/TBD | Not started | - |
