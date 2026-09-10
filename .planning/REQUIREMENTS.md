# Requirements: LoopLift

**Defined:** 2026-09-10  
**Core Value:** LoopLift automatically decides whether a supported loop remains safe to parallelize across helper-function calls and explains the evidence behind that decision.

## v1 Requirements

### Input and Frontend

- [ ] **INPT-01**: User can analyze one existing `.c` source file from the command line.
- [ ] **INPT-02**: User can override the Clang executable used to produce the AST.
- [ ] **INPT-03**: User receives a clear non-zero error for an invalid path, non-C input, missing Clang, or invalid C program.
- [ ] **INPT-04**: User's source is parsed through Clang's JSON AST without executing the compiled program.

### Interprocedural Analysis

- [ ] **ANLY-01**: User can see locally defined functions and direct call-graph edges.
- [ ] **ANLY-02**: User can see every discovered `for` loop with its containing function and source line.
- [ ] **ANLY-03**: User can see direct function-effect summaries for global writes, pointer mutation risk, unknown calls, and unsupported control flow.
- [ ] **ANLY-04**: User can see transitive unsafety propagated through locally defined helper calls, including a call-chain explanation.
- [ ] **ANLY-05**: User receives a conservative result for recursive call cycles rather than an unbounded analysis or unsafe approval.

### Classification and Reporting

- [ ] **CLSF-01**: User can see whether each loop is `safe`, `unsafe`, or `unsupported` for automatic parallelization.
- [ ] **CLSF-02**: User can see stable reason codes and human-readable evidence for every non-safe decision.
- [ ] **CLSF-03**: User only receives a `safe` decision for a documented canonical loop with no detected cross-iteration or transitive side-effect hazard.
- [ ] **RPRT-01**: User receives `analysis.json` containing functions, calls, loops, effects, decisions, and tool metadata.
- [ ] **RPRT-02**: User receives `report.md` and a concise terminal summary suitable for a faculty demo.
- [ ] **QUAL-01**: Maintainer can verify safe, unsafe, transitive-unsafe, recursive, reporting, and CLI behavior through automated tests.

### Transformation

- [ ] **TRNS-01**: User can transform approved loops with `#pragma omp target teams distribute parallel for`.
- [ ] **TRNS-02**: User receives a transformed `.c` file while original source text remains unchanged.
- [ ] **TRNS-03**: Rejected and unsupported loops are never modified.
- [ ] **TRNS-04**: User can preview transformations through a dry-run or manifest before using the output.

### Profitability, Validation, and Demo

- [ ] **PROF-01**: User can see a deterministic profitability decision based on loop-trip and work heuristics.
- [ ] **PROF-02**: User can explicitly override the profitability rejection for experimentation.
- [ ] **VALD-01**: User can compile-check transformed code when a compatible OpenMP toolchain is available.
- [ ] **DEMO-01**: User can open a self-contained HTML explanation generated from an existing analysis report.
- [ ] **DEMO-02**: User can inspect a pre-generated example without requiring GPU hardware.

## v2 Requirements

### Advanced Analysis

- **ADVN-01**: User can analyze multiple translation units.
- **ADVN-02**: User can use richer alias and dependence analysis for more pointer-heavy loops.
- **ADVN-03**: User can target CUDA or HIP directly.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Arbitrary C parallelization | Requires production-grade alias, dependence, and control-flow analysis |
| ML profitability predictor | Needs a trustworthy benchmark dataset and makes the project harder to explain |
| Public compilation service | Requires untrusted-code sandboxing |
| Guaranteed GPU execution on macOS | The local toolchain may not provide an OpenMP target runtime |
| Automatic transformation of ambiguous code | Conservative rejection protects correctness |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INPT-01 | Phase 1 | Pending |
| INPT-02 | Phase 1 | Pending |
| INPT-03 | Phase 1 | Pending |
| INPT-04 | Phase 1 | Pending |
| ANLY-01 | Phase 1 | Pending |
| ANLY-02 | Phase 1 | Pending |
| ANLY-03 | Phase 1 | Pending |
| ANLY-04 | Phase 1 | Pending |
| ANLY-05 | Phase 1 | Pending |
| CLSF-01 | Phase 1 | Pending |
| CLSF-02 | Phase 1 | Pending |
| CLSF-03 | Phase 1 | Pending |
| RPRT-01 | Phase 1 | Pending |
| RPRT-02 | Phase 1 | Pending |
| QUAL-01 | Phase 1 | Pending |
| TRNS-01 | Phase 2 | Pending |
| TRNS-02 | Phase 2 | Pending |
| TRNS-03 | Phase 2 | Pending |
| TRNS-04 | Phase 2 | Pending |
| PROF-01 | Phase 3 | Pending |
| PROF-02 | Phase 3 | Pending |
| VALD-01 | Phase 3 | Pending |
| DEMO-01 | Phase 3 | Pending |
| DEMO-02 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-10*
*Last updated: 2026-09-10 after the P05 scope pivot*
