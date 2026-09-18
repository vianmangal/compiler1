import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile, FileBlob } from '@oai/artifact-tool';
import { finalizePresentation, resolvePresentationFont } from '/Users/vian/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.22227/skills/presentations/container_tools/artifact_tool_utils.mjs';

const root = '/Users/vian/Documents/ChatGPT/compiler-lab';
const build = path.join(root, 'tmp/presentations/review1');
const skill = '/Users/vian/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.22227/skills/presentations';
const python = '/Users/vian/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const final = path.join(root, 'output/presentations/Compiler_Lab_Review_1.pptx');
await fs.mkdir(path.dirname(final), { recursive: true });
const font = resolvePresentationFont({ fontFamily: 'Helvetica' });
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
function text(slide, value, x, y, w, h, size = 29, bold = false) {
  const shape = slide.shapes.add({ geometry: 'textbox', position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
  shape.text = value;
  shape.text.style = { typeface: font, fontSize: size, bold, color: '#000000', autoFit: 'none' };
  return shape;
}
function slide(title, rows, notes) {
  const s = deck.slides.add();
  s.background.fill = '#FFFFFF';
  text(s, title, 90, 60, 1100, 85, 48, true);
  rows.forEach((r, i) => text(s, r, 90, 185 + i * 110, 1090, 90));
  s.speakerNotes.textFrame.setText(notes);
  return s;
}
const cover = deck.slides.add();
cover.background.fill = '#FFFFFF';
text(cover, 'Compiler Lab Project', 115, 215, 1100, 100, 64, true);
text(cover, 'Vian Mangal', 115, 360, 1000, 70, 36);
text(cover, '24BAI0134', 115, 430, 1000, 70, 36);
cover.speakerNotes.textFrame.setText('Review 1: project proposal, design, and initial implementation. Project topic: LLVM Pass Transformation Analyzer.');

slide('Topic and Problem Statement', [
  'Topic: LLVM Pass Transformation Analyzer\nSegfault P01, under Explainable Compilers.',
  'Problem: LLVM produces many optimization pass dumps.\nFinding which passes changed the code is difficult.',
  'Motivation: Help students understand optimization\nwithout reading a long compiler log.',
  'Why this topic: A small local project using Clang.\nNo GPU, database, or AI model is required.'
], 'Source: docs/PRD.md, sections 1–3 and 8. LLVM IR means intermediate representation. The tool observes existing compiler passes rather than implementing a new compiler.');

slide('Objectives and Scope', [
  'Capture LLVM IR snapshots from a small C program\nusing the Clang optimization pipeline.',
  'Identify the pass name, scope, and execution order.\nKeep snapshots that change the IR.',
  'Planned output: A readable transformation timeline\nwith saved IR snapshots and a JSON manifest.',
  'Scope: Local analysis of small C files.\nNo program execution, GPU support, or public server.'
], 'Source: docs/PRD.md, sections 4–8. These are project objectives. The CLI and report outputs remain pending, as shown on the final slide.');

slide('Background and Compiler Concepts', [
  'Background study: Clang can expose LLVM pass dumps.\nThe analyzer organizes these dumps into useful changes.',
  'Frontend: Clang handles lexical analysis, parsing,\nand semantic checks for the input C program.',
  'Intermediate representation: LLVM IR describes\nprogram operations before final machine code.',
  'Optimization passes: Compare consecutive IR states\nwithin the same function or module scope.'
], 'Sources: docs/PRD.md, .planning/phases/01-cli-transformation-pipeline/01-CONTEXT.md, iris_analyzer/parser.py, and iris_analyzer/compiler.py. The analyzer does not implement its own lexer, parser for C, or optimization passes. Its parser reads LLVM dump sections.');

slide('System Design and Methodology', [
  '1. Input and compiler capture\nResolve Clang and capture its optimization pass output.',
  '2. Snapshot parser\nExtract pass names, scopes, ordering, and IR text.',
  '3. Change filtering\nNormalize formatting and compare snapshots per scope.',
  '4. Reporting, planned\nWrite the retained timeline and snapshots to files.'
], 'Sources: iris_analyzer/compiler.py, iris_analyzer/parser.py, iris_analyzer/model.py, docs/IMPLEMENTATION_PLAN.md. Data flow: C source into Clang, pass dump into parser, snapshots into change filter, retained snapshots into a future report writer. Implemented modules: compiler, parser, and model. Reporting and command-line integration remain pending.');

slide('Technology Stack and Initial Prototype', [
  'Python 3.10+ and its standard library\nNo external Python package is required for the analyzer.',
  'Clang and LLVM\nThe compiler wrapper requests IR dumps at -O1.',
  'Working prototype: Compiler wrapper and IR parser.\nIt filters unchanged dumps and limits retained snapshots.',
  'Error handling: Missing compiler, launch failures,\ncompilation errors, and a 30-second timeout.'
], 'Sources: iris_analyzer/compiler.py, parser.py, model.py, tests/test_compiler.py, and tests/test_parser.py. subprocess uses shell=False. Compiler diagnostics are bounded to 4,000 characters. No finished command-line application or report generation is claimed.');

slide('Testing, Progress and Next Steps', [
  'Test result: All 21 unit tests pass.\nCoverage includes parsing, filtering, and compiler errors.',
  'Completed: Proposal, PRD, implementation plan,\nand the initial compiler-capture and parsing modules.',
  'Pending: CLI, JSON and Markdown reports,\nsaved IR files, and a real Clang integration demo.',
  'Conclusion: The core prototype is ready to extend.\nThe full Phase 1 workflow is still in progress.'
], 'Evidence: python3 -m unittest discover -s tests -v passes 21 tests on 2026-09-18. The compiler boundary tests mock subprocess execution. A real end-to-end Clang demo has not yet been completed. Supporting documents: docs/PRD.md, docs/IMPLEMENTATION_PLAN.md, and output/pdf/LLVM_Pass_Transformation_Analyzer_Proposal.pdf (tracked version).');

const candidate = path.join(build, 'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidate);
await finalizePresentation({
  workspaceDir: root, candidatePath: candidate, finalPath: final,
  pythonExecutable: python,
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-heading-fit'],
  explicitTotalSlideCount: 7,
  requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'user_request', families: ['Helvetica'] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(build, 'validation.json')
});
const checkedDeck = await PresentationFile.importPptx(await FileBlob.load(final));
for (let i = 0; i < checkedDeck.slides.items.length; i++) {
  const image = await checkedDeck.export({ slide: checkedDeck.slides.items[i], format: 'png', scale: 1 });
  await fs.writeFile(path.join(build, `slide-${i + 1}.png`), new Uint8Array(await image.arrayBuffer()));
}
console.log(final);
