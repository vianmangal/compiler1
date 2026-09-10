# Requirements: IRis

**Defined:** 2026-09-10  
**Core Value:** A user can run one command and clearly see which LLVM passes changed their program's IR.

## v1 Requirements

### Input and Toolchain

- [ ] **INPUT-01**: User can analyze one existing C source file from the command line.
- [ ] **INPUT-02**: User receives a clear error when the source path, extension, or Clang toolchain is invalid.
- [ ] **INPUT-03**: User can override the Clang executable used for analysis.

### Transformation Capture

- [ ] **CAPT-01**: User can run the source through Clang's LLVM `-O1` optimization pipeline.
- [ ] **CAPT-02**: User can see the ordered pass name, IR scope, and IR body for captured dumps.
- [ ] **CAPT-03**: User sees only changed consecutive snapshots within each IR scope.
- [ ] **CAPT-04**: User can cap the number of retained snapshots for predictable report size.

### Reporting

- [ ] **RPRT-01**: User receives a JSON manifest describing the analysis and retained snapshots.
- [ ] **RPRT-02**: User receives a readable Markdown timeline of retained transformations.
- [ ] **RPRT-03**: User receives each retained IR snapshot as a numbered `.ll` file.
- [ ] **RPRT-04**: User sees a concise terminal summary with the report location.

### Quality

- [ ] **QUAL-01**: User can follow README instructions to analyze the included example.
- [ ] **QUAL-02**: Maintainer can verify parser, filtering, reporting, CLI validation, and local Clang integration through automated tests.

## v2 Requirements

### Explanation

- **EXPL-01**: User can see plain-English descriptions for common LLVM passes.
- **EXPL-02**: User can see line-addition and line-removal counts between comparable snapshots.
- **EXPL-03**: User can inspect a unified diff for a selected transformation.

### Visualization

- **VIS-01**: User can open a generated report in a local browser timeline.
- **VIS-02**: User can select a pass and compare adjacent IR in two panes.
- **VIS-03**: User can filter transformations by function or pass name.

## Out of Scope

| Feature | Reason |
|---------|--------|
| AI optimization recommendations | Requires training/evaluation and weakens the simple deterministic story |
| GPU/OpenCL support | Hardware-dependent and belongs to different problem statements |
| Arbitrary language frontends | C provides enough examples for the MVP |
| Public compilation service | Requires sandboxing untrusted code |
| Custom LLVM passes | The project explains existing passes rather than implementing an optimizer |

## Traceability

Roadmap creation will map each v1 requirement to exactly one phase.

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 0
- Unmapped: 13 ⚠️

---
*Requirements defined: 2026-09-10*
*Last updated: 2026-09-10 after initial definition*
