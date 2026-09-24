# IRis — LLVM Pass Transformation Analyzer

IRis is a small compiler-design lab project that shows which LLVM optimization passes actually changed a C program's intermediate representation (IR). It uses the installed Clang pipeline and produces a report that is easy to inspect or demonstrate.

## Requirements

- Python 3.10 or newer
- Clang available as `clang` on `PATH`
- No third-party Python packages

Check the compiler with:

```sh
clang --version
```

## First run

From the repository root, run:

```sh
python3 -m iris_analyzer analyze examples/loop.c
```

The command prints the retained transformation count and the absolute report location. By default it creates `./loop-iris-report`.

## Options

- `SOURCE` — exactly one existing file with a lower-case `.c` extension.
- `--clang EXECUTABLE` — use a specific Clang path or command name instead of `clang` from `PATH`.
- `--output DIRECTORY` — choose the report directory instead of `./SOURCE_STEM-iris-report`.
- `--max-snapshots N` — retain at most `N` changed snapshots; the default is `50` and `N` must be positive.

Example with every option:

```sh
python3 -m iris_analyzer analyze examples/loop.c \
  --clang clang \
  --output demo-report \
  --max-snapshots 25
```

## Report layout

```text
loop-iris-report/
├── manifest.json
├── timeline.md
└── snapshots/
    ├── 001-pass-name.ll
    └── 002-pass-name.ll
```

- `manifest.json` records the source, compiler, exact command, counts, cap, truncation state, and snapshot metadata.
- `timeline.md` lists retained transformations in order with links to their LLVM IR.
- `snapshots/*.ll` contains one numbered file for each retained transformation.

IRis never deletes or overwrites a non-empty output directory. Choose a new directory or empty the old one yourself before regenerating a report.

## Tests

Run the complete standard-library test suite from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

The real-Clang integration test skips only when `clang` is not installed.

## Current boundary

This version accepts local C files only. It compiles them to inspect LLVM IR but never runs the compiled program. It does not yet provide pass explanations, source/IR diffs, or a browser interface; those are reserved for later phases.
