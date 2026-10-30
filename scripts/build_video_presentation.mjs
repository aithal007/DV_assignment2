import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const workspaceDir=ROOT;
const OUT=path.join(ROOT,'output/video_presentation');
const TMP=path.join(ROOT,'tmp/video_build');
const runtimeBase='C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const modules=path.join(runtimeBase,'node/node_modules');
process.env.RUNTIME_NODE_MODULES=modules;
const SKILL='C:/Users/Parikshith/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const req=createRequire(path.join(modules,'__runtime__.cjs'));
const {Presentation,PresentationFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const {GlobalFonts}=req('@napi-rs/canvas');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arial.ttf','Arial');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arialbd.ttf','Arial');
const sharp=req('sharp');
const STORY=JSON.parse(await fs.readFile(path.join(OUT,'storyboard.json'),'utf8'));
await fs.mkdir(TMP,{recursive:true});await fs.mkdir(path.join(OUT,'slides'),{recursive:true});
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={ink:'#142D43',muted:'#536574',teal:'#087E8B',orange:'#D66A2C',paper:'#F6F8FA',white:'#FFFFFF',line:'#DCE4EA',navy:'#102B40'};

function rect(sl,x,y,w,h,fill,line='none',lw=0){
 return sl.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,
   line:{fill:line,width:lw,style:'solid'}});
}
function text(sl,value,x,y,w,h,size=24,color=C.ink,bold=false,align='left'){
 const sh=sl.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',
  line:{fill:'none',width:0,style:'solid'}});
 sh.text=value;sh.text.style={typeface:'Arial',fontSize:size,color,bold,alignment:align,
   verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
 return sh;
}
async function img(sl,name,x,y,w,h){
 const file=path.join(OUT,'assets',name),bytes=await fs.readFile(file),meta=await sharp(bytes).metadata();
 const k=Math.min(w/meta.width,h/meta.height),ww=meta.width*k,hh=meta.height*k;
 sl.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),
  contentType:'image/png',alt:name.replaceAll('_',' '),fit:'contain',
  position:{left:x+(w-ww)/2,top:y+(h-hh)/2,width:ww,height:hh}});
}
function base(s){
 const sl=P.slides.add();sl.background.fill=C.paper;
 rect(sl,0,0,1280,7,s.number<=9?C.teal:C.orange);
 if(s.layout!=='cover') text(sl,s.title,52,34,1176,86,35,C.ink,true);
 rect(sl,52,124,1176,1,C.line);
 if(s.layout!=='cover') text(sl,s.source,52,679,1135,31,12,C.muted);
 text(sl,String(s.number).padStart(2,'0'),1190,679,40,25,14,C.muted,false,'right');
 if(s.takeaway){rect(sl,52,609,1176,55,'#E6EFF2');text(sl,s.takeaway,70,621,1140,33,22,C.ink,true);}
 sl.speakerNotes.text=`SPEAKER: ${s.speaker}\nRAW RECORDING: ${stamp(s.start)}–${stamp(s.end)} (${s.duration}s)\n\nNARRATION\n${s.say||'[Silent closing card]'}\n\nSCREEN\n${s.screen}\n\nACTIONS\n${s.actions}\n\nSOURCE\n${s.source}\n\nASSETS\n${s.images.join('\n')}`;
 return sl;
}
function stamp(t){return `${Math.floor(t/60)}:${String(t%60).padStart(2,'0')}`;}
for(const s of STORY.slides){
 const sl=base(s);
 switch(s.layout){
 case 'cover':
  sl.background.fill=C.navy;
  text(sl,'DAS732  /  ASSIGNMENT 2',54,42,620,30,17,'#7CC8CE',true);
  text(sl,'What do averages\nand snapshots hide?',54,128,655,210,55,C.white,true);
  text(sl,'Inequality, relationships and\nchange over time',56,369,630,90,29,'#B9D5E0');
  text(sl,'Country internet indicators and daily weather',56,495,630,70,22,'#B9D5E0');
  rect(sl,754,85,466,244,C.white);await img(sl,'profiles.png',766,104,442,200);
  text(sl,'COUNTRY PROFILES',767,341,420,25,15,'#7CC8CE',true);
  rect(sl,754,387,466,223,C.white);await img(sl,'rainfall.png',766,396,442,203);
  text(sl,'DAILY WEATHER',767,619,420,24,15,'#7CC8CE',true);
  text(sl,'Parikshith Aithal K V   ·   Sindhoor Ganapathi Hegde   ·   Varshith M Gowda',56,656,1160,30,17,C.white);
  break;
 case 'network':
  text(sl,s.headline,52,143,850,38,25,C.teal,true);
  rect(sl,52,194,1176,394,C.white);await img(sl,'network.png',62,200,1156,380);
  break;
 case 'paths':
  text(sl,s.headline,52,143,1176,40,26,C.teal,true);
  await img(sl,'country_paths.png',52,195,1176,395);
  break;
 case 'profiles':
  text(sl,s.headline,52,145,900,45,30,C.teal,true);
  rect(sl,52,211,1176,355,C.white);await img(sl,'profiles.png',64,217,1150,340);
  text(sl,'G1 and G2 are exploratory groups derived from the same four indicators.',62,570,1140,30,17,C.muted);
  break;
 case 'inequality':
  text(sl,s.headline,52,143,1176,42,24,C.ink,true);
  rect(sl,52,195,1176,397,C.white);await img(sl,'inequality.png',64,200,1152,385);
  break;
 case 'matrix':
  text(sl,s.headline,52,143,1176,40,25,C.teal,true);
  await img(sl,'nodetrix_zoom.png',52,195,1176,395);
  break;
 case 'spread':
  text(sl,s.headline,52,143,1176,40,25,C.teal,true);
  await img(sl,'within_regions.png',52,195,1176,395);
  break;
 case 'overlap':
  text(sl,s.headline,52,143,1176,40,25,C.teal,true);
  await img(sl,'intersections.png',52,195,1176,395);
  break;
 case 'regional':
  text(sl,'26.55 pp',56,151,300,53,42,C.teal,true);
  text(sl,'Shift of Asia’s regional median',56,208,320,64,21,C.ink);
  text(sl,'19.75 pp',56,326,300,53,42,C.orange,true);
  text(sl,'Median individual country gain',56,383,320,64,21,C.ink);
  text(sl,'2015–2020 · 41 Asian countries',56,515,320,50,18,C.muted);
  rect(sl,407,150,821,438,C.white);await img(sl,'regional.png',417,157,801,420);
  break;
 case 'temporal':
  text(sl,'Trajectories',52,143,555,35,25,C.teal,true);text(sl,'Distributions',668,143,550,35,25,C.orange,true);
  rect(sl,52,190,560,398,C.white);await img(sl,'horizon.png',58,196,548,385);
  rect(sl,668,190,560,398,C.white);await img(sl,'ridgeline.png',674,196,548,385);
  break;
 case 'pcp':
  text(sl,'6 of 175 countries: adoption ≥70%, fixed broadband ≤5 / 100',52,145,1176,38,25,C.teal,true);
  await img(sl,'pcp.png',52,190,1176,405);
  break;
 case 'treemap':
  text(sl,'Same leaves and total, with a different grouping',52,145,1170,40,25,C.teal,true);
  rect(sl,52,203,730,385,C.white);await img(sl,'treemap.png',62,213,710,365);
  text(sl,'AREA',832,223,340,30,17,C.teal,true);
  text(sl,'Internet users',832,262,350,75,31,C.ink,true);
  text(sl,'COUNTRY COLOUR',832,377,360,30,17,C.orange,true);
  text(sl,'Adoption percentage',832,417,350,90,31,C.ink,true);
  break;
 case 'levels':
  text(sl,'Same 175 countries, different analytical questions',52,145,1170,40,25,C.teal,true);
  rect(sl,52,198,1176,398,C.white);await img(sl,'levels_changes.png',62,204,1156,385);
  break;
 case 'colour':
  text(sl,'Fixed scale',52,145,510,35,26,C.teal,true);text(sl,'Daily scale',650,145,510,35,26,C.orange,true);
  rect(sl,52,190,1176,404,C.white);await img(sl,'colour.png',62,196,1156,390);
  break;
 case 'rainfall':
  rect(sl,52,151,896,440,C.white);await img(sl,'rainfall.png',58,158,884,425);
  text(sl,'44%',980,169,230,78,60,C.teal,true);
  text(sl,'July',980,248,230,35,24,C.ink);
  text(sl,'78%',980,314,230,78,60,C.orange,true);
  text(sl,'September',980,393,230,35,24,C.ink);
  text(sl,'Eligible area receiving\n≥50% of monthly rain\nin five consecutive days',980,458,245,114,20,C.ink);
  break;
 case 'contours':
  text(sl,'Filled contours: same field, different intervals',52,145,1170,40,25,C.teal,true);
  rect(sl,52,193,1176,402,C.white);await img(sl,'contours.png',62,199,1156,390);
  break;
 case 'persistence':
  text(sl,'67 days',52,146,300,70,51,C.orange,true);
  text(sl,'Longest local run in the observed window',365,162,860,48,25,C.ink,true);
  rect(sl,52,229,1176,340,C.white);await img(sl,'persistence.png',60,235,1160,327);
  text(sl,'Hot: Tmax ≥35°C    Dry: rain <1 mm/day    July–September 2023',62,573,1135,28,19,C.muted);
  break;
 case 'quiver':
  text(sl,'Same every-eighth-cell sample, different length encodings',52,145,1170,40,25,C.teal,true);
  rect(sl,52,192,1176,405,C.white);await img(sl,'quiver.png',62,197,1156,395);
  break;
 case 'intersections':
  rect(sl,52,151,890,444,C.white);await img(sl,'intersections.png',60,159,874,428);
  text(sl,'2.57%',973,194,255,80,56,C.orange,true);
  text(sl,'of weighted\narea-days',975,286,250,95,28,C.ink,true);
  text(sl,'Hot + dry + windy',975,418,250,75,25,C.ink,true);
  text(sl,'Daily gridded summaries',975,533,250,52,17,C.muted);
  break;
 case 'conclusion':
  for(const [i,title,evidence,implication] of [
   [0,'Differences behind averages','Country links and spread · Figs. 3, 11–12','Regional averages hide different country experiences.'],
   [1,'Timing behind summaries','Rainfall and persistence · Figs. 23, 30','Totals and counts conceal concentration and uninterrupted runs.'],
   [2,'Overlap behind separate measures','Intersections · Fig. 29; matched-change evidence','Separate frequencies conceal overlap. Level associations do not explain changes.']]){
    const y=151+i*145;
    text(sl,String(i+1).padStart(2,'0'),53,y,75,60,42,i===1?C.orange:C.teal,true);
    text(sl,title,155,y,1050,45,29,C.ink,true);
    text(sl,implication,155,y+46,1040,55,23,C.ink);
    text(sl,evidence,155,y+106,1040,27,15,C.muted);
   }
  break;
 case 'credits':
  text(sl,'Contribution allocation',52,150,1170,40,27,C.teal,true);
  const members=[['Parikshith Aithal K V','BT2024249','Network methods and scalar colour mapping'],
   ['Sindhoor Ganapathi Hegde','BT2024014','Horizon/ridgeline methods and contours'],
   ['Varshith M Gowda','BT2024227','JavaScript PCP/treemap and quiver']];
  members.forEach(([name,id,task],i)=>{const y=216+i*108;text(sl,name,52,y,660,40,28,C.ink,true);text(sl,id,52,y+42,500,28,17,C.muted);text(sl,task,730,y+8,495,74,23,C.ink);});
  rect(sl,52,555,1176,1,C.line);
  text(sl,'Data: OWID/ITU via Assignment 1; gridMET daily weather',52,577,1170,35,22,C.ink);
  text(sl,'Full evidence and references in the report. Browser demo: 127.0.0.1:8765/web/home.html',52,625,1170,35,19,C.muted);
  break;
 }
}
const fontPolicy={basis:'design',families:['Arial']};
const candidatePath=path.join(TMP,'video_candidate.pptx');
if(!process.argv.includes('--finalize-only')){
await (await PresentationFile.exportPptx(P)).save(candidatePath);
await fs.writeFile(path.join(TMP,'presentation.proto.json'),JSON.stringify(P.toProto()));
for(const [i,sl] of P.slides.items.entries()){
 const png=await P.export({slide:sl,format:'png',scale:1.5});
 await fs.writeFile(path.join(OUT,'slides',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
}
const FINAL=path.join(OUT,`DAS732_A2_Video_Presentation_Reviewed_${Date.now()}.pptx`);
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath:FINAL,
 pythonExecutable:path.join(runtimeBase,'python/python.exe'),
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 fontPolicy,explicitTotalSlideCount:17,verifyArtifactToolImport:true,
 receiptPath:path.join(TMP,`video_presentation_${Date.now()}.validation.json`)});
console.log(JSON.stringify(result));
await fs.copyFile(FINAL,path.join(OUT,'DAS732_A2_Video_Presentation_Final.pptx'));
