# Compiler Design Lab

Work-in-progress project backup for Vian Mangal (24BAI0134).

## Saved work

All current work is consolidated on `main`: the LLVM Pass Transformation Analyzer prototype, matching P01 planning, requirements, implementation plans, and the four-page proposal in `output/pdf/`.

The prototype includes LLVM snapshot parsing, compiler integration, fixtures, and 21 unit tests. Earlier LoopLift/P05 planning remains recoverable through Git history rather than a separate branch.

Phase 1 and Review 1 are not yet fully complete. The prototype still needs its CLI, report output, and end-to-end demonstration.

## Prototype tests

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

See `docs/PRD.md`, `docs/IMPLEMENTATION_PLAN.md`, and `.planning/` for scope and progress.
