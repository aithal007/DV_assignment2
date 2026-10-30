// Run against either the staged site under a project subpath or the deployed URL.
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/x.cjs');
const {chromium}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../docs');
const prefix='/DV_assignment2/';let server;
let base=process.argv[2];
if(!base){
  const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css','.png':'image/png','.gif':'image/gif','.pdf':'application/pdf','.csv':'text/csv'};
  server=http.createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');if(!url.pathname.startsWith(prefix))throw Error('prefix');let rel=decodeURIComponent(url.pathname.slice(prefix.length))||'index.html';let target=path.resolve(root,rel);if(!target.startsWith(root+path.sep))throw Error('path');res.setHeader('Content-Type',mime[path.extname(target)]||'application/octet-stream');res.end(await fs.readFile(target));}catch{res.statusCode=404;res.end('Not found');}});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));base=`http://127.0.0.1:${server.address().port}${prefix}`;
}
if(!base.endsWith('/'))base+='/';
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const errors=[],responses=[];const assert=(x,m)=>{if(!x)throw Error(m)};
try{
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('response',r=>{if(r.status()>=400)responses.push(`${r.status()} ${r.url()}`)});
 await page.goto(base,{waitUntil:'networkidle'});assert((await page.title()).includes('Beyond Averages'),'Landing page');
 await page.goto(base+'web/network.html');await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('797 of 15931'));
 await page.locator('#search').fill('India');await page.locator('#find').click();assert((await page.locator('#details').innerText()).includes('12 visible neighbors'),'India links');
 for(const layout of ['Spectral','Circular','Spring'])await page.locator('#layout').selectOption(layout);
 await page.locator('#similarity').fill('0.8');await page.locator('#similarity').dispatchEvent('input');assert(!(await page.locator('#status').innerText()).includes('797 of 15931'),'filter');await page.locator('#reset').click();
 await page.goto(base+'web/index.html');await page.waitForFunction(()=>document.querySelectorAll('.country-line').length===175);const before=await page.locator('.country-line').first().getAttribute('d');await page.locator('#bundle').fill('70');await page.locator('#bundle').dispatchEvent('input');assert(before!==await page.locator('.country-line').first().getAttribute('d'),'bundling');
 await page.goto(base+'web/treemap.html');await page.waitForFunction(()=>document.querySelectorAll('g.tile').length>0);await page.locator('g.tile[aria-label^="Asia,"]').click();assert((await page.locator('#crumb').innerText()).includes('Asia'),'zoom');await page.locator('#back').click();await page.locator('#hierarchy').selectOption('adoption');
 await page.goto(base+'output/pcp_changes/index.html');await page.waitForFunction(()=>document.querySelectorAll('#chart path.line').length>100);await page.locator('#reorder').click();
 await page.goto(base+'figures.html');assert(await page.locator('article').count()===32,'32 figure cards');
 await page.goto(base+'output/network_revision/index.html');assert((await page.title()).includes('Network method'),'research page');
 for(const asset of ['output/pdf/DAS732_A2_Report_IEEE.pdf','images/scivis/scivis_contour.gif','images/scivis/scivis_global.gif','images/scivis/scivis_local.gif','images/report/Fig31.png','images/report/Fig32.png']){const r=await page.request.get(base+asset);assert(r.ok(),`asset ${asset} ${r.status()}`);}
 assert(!errors.length,errors.join('; '));assert(!responses.length,responses.join('; '));
 console.log(JSON.stringify({base,network_layouts:3,india_neighbors:12,threshold_filter:true,parallel_coordinates:175,treemap_zoom:true,paired_changes:true,figure_cards:32,report_and_gifs:true,errors},null,2));
}finally{await browser.close();if(server)server.close()}
