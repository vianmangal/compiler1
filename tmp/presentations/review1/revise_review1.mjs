import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
import { finalizePresentation, makeNativeBulletParagraphs } from '/Users/vian/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.22227/skills/presentations/container_tools/artifact_tool_utils.mjs';

const root = '/Users/vian/Documents/ChatGPT/compiler-lab';
const build = path.join(root, 'tmp/presentations/review1/revised');
const skill = '/Users/vian/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.22227/skills/presentations';
const finalPath = path.join(root, 'output/presentations/Compiler_Lab_Review_1_Updated.pptx');
await fs.mkdir(build, {recursive: true});
const deck = await PresentationFile.importPptx(await FileBlob.load(path.join(root, 'output/presentations/Compiler_Lab_Review_1.pptx')));
const snapshot = await deck.inspect({kind: 'slide,textbox,layout', maxChars: 50000});
await fs.writeFile(path.join(build, 'before.ndjson'), snapshot.ndjson);
const records = snapshot.ndjson.trim().split('\n').map(line => JSON.parse(line));

const replacements = {
  2: [
    'Topic: LLVM Pass Transformation Analyzer',
    'The compiler improves code through many steps.\nIt is hard to tell which steps changed the code.',
    'Why this topic: A small local project using Clang.\nNo GPU, database, or AI model is required.'
  ],
  7: [
    'Parsing tests check pass names, order, and IR text.\nThey also check empty logs and different dump formats.',
    'Filtering tests check that unchanged IR is skipped.\nThey check separate scopes and snapshot limits.',
    'Compiler tests simulate Clang to check discovery,\nsafe commands, error handling, and timeouts.',
    'Results: All 21 unit tests passed. None failed.\nThe CLI, report files, and complete demo remain pending.'
  ]
};
for (const slideRecord of records.filter(r => r.kind === 'slide' && r.slide > 1)) {
  const number = slideRecord.slide;
  const body = records.filter(r => r.kind === 'textbox' && r.slide === number && r.bbox[1] > 145).sort((a,b) => a.bbox[1] - b.bbox[1]);
  const rows = replacements[number] ?? body.map(r => r.text.replace(/^\d+\.\s*/, ''));
  body.forEach((record, index) => {
    const shape = deck.resolve(record.id);
    if (index >= rows.length) { shape.text = ''; return; }
    shape.text = makeNativeBulletParagraphs([rows[index]], {marginLeftPoints: 18, hangingPoints: 9, spaceAfterPoints: 0});
    shape.text.style = {typeface: 'Helvetica', fontSize: 29, color: '#000000', autoFit: 'none'};
    if (number === 2) shape.position = {left: 90, top: 185 + index * 145, width: 1090, height: 100};
  });
  if (number === 7) {
    const title = records.find(r => r.kind === 'textbox' && r.slide === 7 && r.bbox[1] === 60);
    deck.resolve(title.id).text = 'Testing and Results';
    deck.resolve(slideRecord.id).speakerNotes.textFrame.setText('Evidence: python3 -m unittest discover -s tests -v, 21 tests passed on 2026-09-18. Sources: tests/test_parser.py and tests/test_compiler.py. Parser tests include immutable model contracts, whitespace normalization, empty input, banner variants, ordering, per-scope change filtering, and cap behavior. Compiler tests use mocks to check executable discovery, command construction, compiler output capture, errors, and timeout handling. A real end-to-end compiler demonstration and the CLI/report writer are still pending.');
  }
}
const candidatePath = path.join(build, 'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
await finalizePresentation({
  workspaceDir: root, candidatePath, finalPath,
  pythonExecutable: '/Users/vian/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry'],
  explicitTotalSlideCount: 7,
  requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
  fontPolicy: {basis: 'user_request', families: ['Helvetica']},
  verifyArtifactToolImport: true, receiptPath: path.join(build, 'validation.json')
});
const checked = await PresentationFile.importPptx(await FileBlob.load(finalPath));
await fs.writeFile(path.join(build, 'after.ndjson'), (await checked.inspect({kind:'slide,textbox,notes,layout',maxChars:50000})).ndjson);
for (let i = 0; i < checked.slides.items.length; i++) {
  const png = await checked.export({slide: checked.slides.items[i], format: 'png', scale: 1});
  await fs.writeFile(path.join(build, `slide-${i+1}.png`), new Uint8Array(await png.arrayBuffer()));
}
console.log(finalPath);
