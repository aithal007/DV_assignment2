import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import {pathToFileURL,fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const skill='C:/Users/Parikshith/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';
const runtime='C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const tmp=path.join(root,'tmp/network_video'),original=path.join(tmp,'original_deck.pptx');
const dest=path.join(root,'output/video_presentation/DAS732_A2_Video_Presentation_Final.pptx');
try{await fs.access(original)}catch{await fs.copyFile(dest,original)}
const finalPath=path.join(root,'output/video_presentation',`DAS732_A2_Network_Reviewed_${Date.now()}.pptx`);
const r=await finalizePresentation({workspaceDir:root,candidatePath:path.join(tmp,'merged_candidate.pptx'),finalPath,
 pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 fontPolicy:{basis:'reference',families:['Segoe UI'],referencePath:original,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(original)).digest('hex')},explicitTotalSlideCount:14,verifyArtifactToolImport:true,receiptPath:path.join(tmp,`validation_${Date.now()}.json`)});
console.log(JSON.stringify(r));await fs.copyFile(finalPath,dest);
