import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL='C:/Users/Parikshith/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const runtime='C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
process.env.RUNTIME_NODE=path.join(runtime,'node/bin/node.exe');
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const candidatePath=path.join(ROOT,'tmp/video_build/focused_story_candidate.pptx');
const finalPath=path.join(ROOT,'output/video_presentation',`DAS732_A2_Focused_Story_Reviewed_${Date.now()}.pptx`);
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath,finalPath,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 explicitTotalSlideCount:14,requiredNativeChartOwnerSlides:[],requiredEmbeddedWorkbookChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Segoe UI','Segoe UI Light']},verifyArtifactToolImport:true,
 receiptPath:path.join(ROOT,`presentation_source/focused_story_ppt169_20261024/validation/final_presentation_validation_${Date.now()}.json`)});
await fs.writeFile(path.join(ROOT,'presentation_source/focused_story_ppt169_20261024/validation/final_path.json'),JSON.stringify({finalPath,result},null,2));
console.log(JSON.stringify(result));
