import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {FileBlob, PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation, makeNativeBulletParagraphs} from '/Users/vian/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.22227/skills/presentations/container_tools/artifact_tool_utils.mjs';

const root = '/Users/vian/Documents/ChatGPT/compiler-lab';
const build = path.join(root, 'tmp/presentations/review1/expanded');
const skill = '/Users/vian/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.22227/skills/presentations';
const finalPath = path.join(root, 'output/presentations/Compiler_Lab_Review_1_Updated_v2.pptx');
await fs.mkdir(build,{recursive:true});
const deck = await PresentationFile.importPptx(await FileBlob.load(path.join(root,'output/presentations/Compiler_Lab_Review_1_Updated.pptx')));
const before = await deck.inspect({kind:'slide,textbox',maxChars:50000});
const records = before.ndjson.trim().split('\n').map(JSON.parse);
const matches = records.filter(r=>r.kind==='textbox' && r.slide===2 && r.text==='The compiler improves code through many steps.\nIt is hard to tell which steps changed the code.');
if(matches.length!==1) throw Error('Expected exactly one approved problem bullet.');
const shape = deck.resolve(matches[0].id);
shape.text = makeNativeBulletParagraphs([
  'The compiler improves code in steps called optimization passes.\nIts long log includes steps that leave the code unchanged.\nThis makes it hard to see which steps actually changed the code.'
],{marginLeftPoints:18,hangingPoints:9,spaceAfterPoints:0});
shape.text.style={typeface:'Helvetica',fontSize:29,color:'#000000',autoFit:'none'};
shape.position={left:90,top:330,width:1090,height:130};
const candidatePath=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
await finalizePresentation({
  workspaceDir:root,candidatePath,finalPath,
  pythonExecutable:'/Users/vian/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry'],
  explicitTotalSlideCount:7,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
  fontPolicy:{basis:'user_request',families:['Helvetica']},verifyArtifactToolImport:true,
  receiptPath:path.join(build,'validation.json')
});
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
const unchanged=[];
for(let i=0;i<final.slides.items.length;i++){
  const png=await final.export({slide:final.slides.items[i],format:'png',scale:1});
  const bytes=new Uint8Array(await png.arrayBuffer());
  await fs.writeFile(path.join(build,`slide-${i+1}.png`),bytes);
  if(i!==1){
    const old=await fs.readFile(path.join(root,`tmp/presentations/review1/revised/slide-${i+1}.png`));
    const hash=b=>createHash('sha256').update(b).digest('hex');
    if(hash(old)!==hash(bytes))throw Error(`Unrequested visual change on slide ${i+1}`);
    unchanged.push(i+1);
  }
}
console.log(JSON.stringify({finalPath,unchangedSlides:unchanged}));
