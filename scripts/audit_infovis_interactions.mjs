// Exercise the submitted local apps through real browser controls.
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/x.cjs');
const {chromium}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css'};
const server=http.createServer(async(req,res)=>{try{const target=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));if(!target.startsWith(root+path.sep))throw Error('path');res.setHeader('Content-Type',mime[path.extname(target)]||'application/octet-stream');res.end(await fs.readFile(target));}catch{res.statusCode=404;res.end('Not found');}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const proof=path.join(root,'images/gui');await fs.mkdir(proof,{recursive:true});
const result={checked:'2026-10-30',errors:[]};
const assert=(value,message)=>{if(!value)throw Error(message);};
try{
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 page.on('pageerror',e=>result.errors.push(String(e)));
 await page.goto(origin+'/web/network.html');
 await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('797 of 15931'));
 await page.locator('#search').fill('India');await page.locator('#find').click();
 const layouts=await page.locator('#layout option').allTextContents();
 const observations=[];
 for(const layout of layouts){await page.locator('#layout').selectOption(layout);await page.screenshot({path:path.join(proof,'network_'+layout.toLowerCase()+'.png'),fullPage:true});observations.push({layout,status:await page.locator('#status').innerText(),details:await page.locator('#details').innerText()});}
 assert(layouts.length>=3,'Three network layouts missing');
 assert(observations.every(x=>x.status.includes('797')&&x.status.includes('15931')&&x.details.includes('India')),'Network selection/layout failed');
 await page.locator('#similarity').fill('0.8');await page.locator('#similarity').dispatchEvent('input');
 const filtered=await page.locator('#status').innerText();assert(!filtered.includes('797 of 15931'),'Network filter ineffective');
 await page.locator('#similarity').fill('0');await page.locator('#similarity').dispatchEvent('input');
 assert((await page.locator('#status').innerText()).includes('15931 of 15931'),'Complete all-pair graph unavailable');
 await page.locator('#reset').click();assert((await page.locator('#status').innerText()).includes('797 of 15931'),'Default threshold reset failed');
 result.network={layouts,observations,filter:filtered,passed:true};

 await page.goto(origin+'/web/index.html?year=2020&bundle=0&matched=1&fixed=1');
 await page.waitForFunction(()=>document.querySelectorAll('.country-line').length===175);
 const axisValuesBefore=await page.locator('.country-line').evaluateAll(nodes=>nodes.map(n=>[n.dataset.code,n.dataset.values]));
 const straight=await page.locator('.country-line').first().getAttribute('d');
 await page.locator('#bundle').fill('50');await page.locator('#bundle').dispatchEvent('input');
 const bundled=await page.locator('.country-line').first().getAttribute('d');assert(straight!==bundled,'Bundling failed');
 const axisValuesAfter=await page.locator('.country-line').evaluateAll(nodes=>nodes.map(n=>[n.dataset.code,n.dataset.values]));assert(JSON.stringify(axisValuesBefore)===JSON.stringify(axisValuesAfter),'Bundling changed measured axis values');
 await page.locator('.country-line').first().dispatchEvent('mouseenter');assert((await page.locator('#details').innerText()).includes('Internet users'),'Country tooltip missing');
 await page.screenshot({path:path.join(proof,'pcp_bundled.png'),fullPage:true});
 await page.locator('#focus').click();await page.screenshot({path:path.join(proof,'pcp_brush.png'),fullPage:true});const selection=await page.locator('#selection-summary').innerText();assert((await page.locator('#status').innerText()).startsWith('6 of 175'),'Six-country preset failed');
 await page.locator('#clear').click();
 const zone=page.locator('.brush-zone').first();const box=await zone.boundingBox();
 await page.mouse.move(box.x+box.width/2,box.y+box.height*.1);await page.mouse.down();await page.mouse.move(box.x+box.width/2,box.y+box.height*.3,{steps:12});await page.mouse.up();
 assert(await page.locator('.brush').count()>0,'Pointer brush failed');
 const brushed=await page.locator('#selection-summary').innerText();
 const before=await page.locator('.axis-title').allTextContents();await page.locator('.axis-title').first().click();const after=await page.locator('.axis-title').allTextContents();
 assert(before.join('|')!==after.join('|'),'Axis reordering failed');
 result.parallel_coordinates={countries:175,bundling_changes_paths:true,axis_values_unchanged:true,hover_values_checked:true,preset:selection,pointer_brush:brushed,axis_order_before:before,axis_order_after:after,passed:true};

 await page.goto(origin+'/web/treemap.html');
 await page.waitForFunction(()=>document.querySelectorAll('g.tile').length>0);
 await page.screenshot({path:path.join(proof,'treemap_region.png'),fullPage:true});const regionRoot=await page.locator('#status').innerText();
 await page.locator('g.tile[aria-label^="Asia,"]').click();
 await page.screenshot({path:path.join(proof,'treemap_zoom.png'),fullPage:true});const zoomed=await page.locator('#crumb').innerText();assert(zoomed.includes('Asia'),'Treemap zoom failed');
 await page.locator('#back').click();const returned=await page.locator('#status').innerText();assert(returned===regionRoot,'Treemap back failed');
 await page.locator('#hierarchy').selectOption('adoption');const adoptionRoot=await page.locator('#status').innerText();
 await page.screenshot({path:path.join(proof,'treemap_adoption.png'),fullPage:true});
 assert(regionRoot.split(' internet users')[0]===adoptionRoot.split(' internet users')[0],'Hierarchy changed root user total');
 result.treemap={regionRoot,zoomed,adoptionRoot,zoom_and_back:true,hierarchies:2,passed:true};
 const capture=await browser.newPage({viewport:{width:1500,height:900},deviceScaleFactor:2});
 for(const [name,bundle] of [['pcp_browser_straight',0],['pcp_browser_gentle',35]]){
   await capture.goto(origin+'/web/index.html?year=2020&bundle='+bundle+'&matched=1&fixed=1&report=1');
   await capture.waitForFunction(()=>document.querySelectorAll('.country-line').length===175);
   await capture.locator('.chart-wrap').screenshot({path:path.join(root,'output/internet_revision',name+'.png')});
 }
 await capture.close();
 assert(result.errors.length===0,'Browser runtime errors');
 await fs.mkdir(path.join(root,'output/infovis_audit_20261026'),{recursive:true});
 await fs.writeFile(path.join(root,'output/infovis_audit_20261026/interactions.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result,null,2));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
