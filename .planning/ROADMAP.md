# Roadmap: IRis

## Overview

IRis progresses from a complete command-line analyzer that proves the core explainable-compiler workflow, through richer explanations and comparisons, to a lightweight visual timeline for the hackathon demonstration. Phase 1 is the v1 MVP and covers every current v1 requirement; Phases 2 and 3 organize the explicitly deferred v2 capabilities.

## Phases

- [x] **Phase 1: CLI Transformation Pipeline** - Analyze a C file end to end and emit a deterministic, inspectable LLVM transformation report. (completed 2026-09-24)
- [ ] **Phase 2: Explain and Compare** - Make retained transformations understandable through descriptions, metrics, diffs, and filters.
- [ ] **Phase 3: Visual Timeline** - Present generated reports as an interactive local-browser demonstration.

## Phase Details

### Phase 1: CLI Transformation Pipeline

**Goal**: Users can run one command to convert a local C file into a trustworthy timeline of the LLVM passes that changed its IR.
**Depends on**: Nothing (first phase)
**Requirements**: INPUT-01, INPUT-02, INPUT-03, CAPT-01, CAPT-02, CAPT-03, CAPT-04, RPRT-01, RPRT-02, RPRT-03, RPRT-04, QUAL-01, QUAL-02
**Success Criteria** (what must be TRUE):

  1. User can analyze an existing `.c` file from the command line with the discovered Clang executable or an explicit Clang override.
  2. User receives a clear, non-zero error when the source path, extension, toolchain, or compilation is invalid.
  3. User can run Clang's LLVM `-O1` pipeline and inspect ordered pass names, IR scopes, and IR bodies, with unchanged consecutive snapshots filtered per scope and retained output bounded by a configurable cap.
  4. User receives a deterministic report containing `manifest.json`, a readable Markdown timeline, numbered `.ll` snapshots, and a concise terminal summary that identifies the report location.
  5. A first-time user can follow the README to analyze the included example, while a maintainer can verify parsing, filtering, reporting, CLI validation, and local-Clang integration through automated tests.

**Plans**: TBD

### Phase 2: Explain and Compare

**Goal**: Users can understand what changed at each retained transformation without needing prior knowledge of LLVM passes.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: EXPL-01, EXPL-02, EXPL-03, VIS-03 (v2, deferred)
**Success Criteria** (what must be TRUE):

  1. User can see a plain-English description when a retained transformation is produced by a common LLVM pass.
  2. User can see line-addition and line-removal counts and inspect a unified diff between comparable snapshots.
  3. User can filter retained transformations by function or pass name to focus the report on relevant changes.

**Plans**: TBD

### Phase 3: Visual Timeline

**Goal**: Users can explore an existing IRis report as a polished local-browser timeline suitable for a short hackathon demonstration.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: VIS-01, VIS-02 (v2, deferred)
**Success Criteria** (what must be TRUE):

  1. User can open a generated IRis report in a local browser and navigate its transformation timeline without rerunning Clang.
  2. User can select a pass and compare adjacent IR snapshots side by side with added and removed lines visually distinguished.

**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. CLI Transformation Pipeline | 2/2 | Complete   | 2026-09-24 |
| 2. Explain and Compare | 0/TBD | Not started | - |
| 3. Visual Timeline | 0/TBD | Not started | - |
