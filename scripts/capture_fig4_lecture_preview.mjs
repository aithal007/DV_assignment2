import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire('C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/x.cjs');
const {chromium}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'output/fig4_lecture_review_20261026');
const protectedFiles=['REPORT.md','data/current_figure_manifest.json','output/pdf/DAS732_A2_Report_IEEE.pdf','output/internet_revision/pcp_gentle_bundles.png'];
const {createHash}=await import('node:crypto');const digest=async f=>createHash('sha256').update(await fs.readFile(path.join(root,f))).digest('hex');const before=await Promise.all(protectedFiles.map(digest));
const server=http.createServer(async(req,res)=>{try{const target=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));if(!target.startsWith(root+path.sep))throw Error();res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.json':'application/json'})[path.extname(target)]||'application/octet-stream');res.end(await fs.readFile(target));}catch{res.statusCode=404;res.end('missing');}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const assert=(x,m)=>{if(!x)throw Error(m)};const errors=[];
try{
 const p=await browser.newPage({viewport:{width:1500,height:1100},deviceScaleFactor:2});p.on('pageerror',e=>errors.push(String(e)));
 await p.goto('http://127.0.0.1:'+server.address().port+'/output/fig4_lecture_review_20261026/index.html');await p.waitForFunction(()=>document.querySelector('#chart')?.dataset.low==='5');
 assert(await p.locator('.line').count()===175,'Missing country profiles');assert(await p.locator('#chart').getAttribute('data-high')==='23','Wrong comparison count');
 await p.locator('#chart').screenshot({path:path.join(out,'candidate_fig4_brushed_pcp.png')});await p.screenshot({path:path.join(out,'full_interactive_preview.png'),fullPage:true});await fs.writeFile(path.join(out,'candidate_fig4_brushed_pcp.svg'),await p.locator('#chart').evaluate(s=>s.outerHTML));
 await p.locator('.line[data-code="CUB"]').dispatchEvent('mouseenter');assert((await p.locator('#details').innerText()).includes('Cuba'),'Hover failed');
 const firstPath=await p.locator('.line[data-code="CUB"]').getAttribute('d');await p.locator('#curves').selectOption('0');assert(await p.locator('.line[data-code="CUB"]').getAttribute('d')!==firstPath,'Straight toggle failed');
 const titles=await p.locator('.axis-title').allTextContents();await p.locator('#reorder').click();assert(JSON.stringify(await p.locator('.axis-title').allTextContents())!==JSON.stringify(titles),'Reorder failed');assert(await p.locator('#chart').getAttribute('data-low')==='5','Reorder changed selection');
 const z=await p.locator('.brush-zone').boundingBox();await p.mouse.move(z.x+z.width/2,z.y+z.height*.15);await p.mouse.down();await p.mouse.move(z.x+z.width/2,z.y+z.height*.25,{steps:10});await p.mouse.up();assert(await p.locator('#lo').inputValue()==='75'&&await p.locator('#hi').inputValue()==='85','Real brush failed');
 await p.locator('#reset').click();assert(await p.locator('#chart').getAttribute('data-low')==='5','Reset failed');
 assert(errors.length===0,'Runtime errors');assert(JSON.stringify(before)===JSON.stringify(await Promise.all(protectedFiles.map(digest))),'Changed selected report');
 const result={status:'PASS',countries:175,adoption_range:[70,85],low_broadband:5,higher_broadband:23,other_gray:147,actual_pointer_brushing:true,axis_reordering:true,hover:true,straight_bundled_toggle:true,reset:true,report_unchanged:true,figure5_unchanged:true,errors};await fs.writeFile(path.join(out,'browser_validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
