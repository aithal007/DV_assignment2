import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const runtime='C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const req=createRequire(path.join(runtime,'node/node_modules/x.cjs'));
const {Presentation,PresentationFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const sharp=req('sharp');const {GlobalFonts}=req('@napi-rs/canvas');GlobalFonts.registerFromPath('C:/Windows/Fonts/segoeui.ttf','Segoe UI');
const OUT=path.join(ROOT,'output/video_presentation'),TMP=path.join(ROOT,'tmp/network_video');
const story=JSON.parse(await fs.readFile(path.join(OUT,'storyboard.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
function text(sl,t,x,y,w,h,size=26,color='#102638',bold=false){let a=sl.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});a.text=t;a.text.style={typeface:'Segoe UI',fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};}
async function image(sl,name,x,y,w,h){let bytes=await fs.readFile(path.join(OUT,'images',name)),m=await sharp(bytes).metadata(),k=Math.min(w/m.width,h/m.height);sl.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:name,fit:'contain',position:{left:x+(w-m.width*k)/2,top:y+(h-m.height*k)/2,width:m.width*k,height:m.height*k}});}
for(const n of [2,3]){
 const s=story.slides[n-1],sl=p.slides.add();sl.background.fill='#F5F2EA';
 text(sl,'INTERNET / COUNTRY SIMILARITY',42,25,1150,25,16,'#087F83',true);
 text(sl,s.title,40,70,1190,85,42,'#102638',true);
 if(n===2){await image(sl,s.images[0],35,170,1210,345);text(sl,'15,931 possible pairs  →  797 retained links',42,540,1190,55,34,'#087F83',true);text(sl,'P95 threshold: 0.569763  |  12 isolated countries retained',42,605,1190,40,25);}
 else{await image(sl,s.images[0],35,170,800,460);text(sl,'93 / 105',870,200,360,85,58,'#087F83',true);text(sl,'pairs retained in group 5',870,290,360,70,25);text(sl,'Full-group degrees',870,382,360,40,23,'#102638',true);text(sl,'Afghanistan: 14\nAngola: 7',870,437,350,110,28);text(sl,'White means below the threshold, not an unmeasured pair.',42,637,1190,35,23,'#087F83',true);}
 text(sl,'Source: report Figs. 1 and 3; all-pair threshold audit. Similar profiles, not physical cables.',42,684,1140,22,12,'#536878');
 sl.speakerNotes.text=`${s.speaker} | ${s.start}-${s.end}s raw\n\n${s.say}\n\nActions: ${s.actions}\n\n${s.source}`;
}
await fs.mkdir(TMP,{recursive:true});await(await PresentationFile.exportPptx(p)).save(path.join(TMP,'replacement_slides.pptx'));
for(const [i,sl] of p.slides.items.entries()){const blob=await p.export({slide:sl,format:'png',scale:1.5});await fs.writeFile(path.join(TMP,`replacement-${i+2}.png`),new Uint8Array(await blob.arrayBuffer()));}
console.log('Authored two editable replacement slides with Artifact Tool.');
