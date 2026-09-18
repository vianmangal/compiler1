# Compiler Design Lab

Work-in-progress project backup for Vian Mangal (24BAI0134).

## Saved work

- `main`: project planning, requirements, implementation plans, and the four-page LLVM Pass Transformation Analyzer proposal in `output/pdf/`.
- `codex/iris-phase1`: LLVM analyzer prototype, including its parser, compiler integration, fixtures, and 21 passing unit tests.

The default branch currently contains LoopLift/P05 planning, while the proposal and prototype cover the earlier LLVM/P01 direction. Both versions are preserved separately; they have not been merged or aligned.

Phase 1 and Review 1 are not yet fully complete. The prototype still needs its CLI, report output, and end-to-end demonstration.

## Prototype tests

On `codex/iris-phase1`, run:

```sh
python3 -m unittest discover -s tests -v
```

See `docs/PRD.md`, `docs/IMPLEMENTATION_PLAN.md`, and `.planning/` on each branch for that version's scope and progress.
