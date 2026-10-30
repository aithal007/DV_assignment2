import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire('C:/Users/Parikshith/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/x.cjs');
const {chromium}=require('playwright');
const PROJECT=path.join(ROOT,'presentation_source/focused_story_ppt169_20261024');
const dest=path.join(PROJECT,'validation/browser');await fs.mkdir(dest,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
try {
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(PROJECT,'index.html')).href,{waitUntil:'domcontentloaded'});
 await page.waitForTimeout(800);
 const count=await page.locator('section.slide').count();
 const geometry=[];
 for(let i=0;i<count;i++){
  await page.evaluate(i=>{const deck=document.getElementById('deck');deck.style.transition='none';deck.style.transform=`translateX(${-i*innerWidth}px)`;},i);
  await page.waitForTimeout(70);
  const issues=await page.locator('section.slide').nth(i).evaluate(el=>{
   const slide=el.getBoundingClientRect(),issues=[];
   for(const item of el.querySelectorAll('[data-design-canvas] > *')){
    const r=item.getBoundingClientRect();if(r.bottom>slide.bottom+1||r.right>slide.right+1||r.left<slide.left-1||r.top<slide.top-1)issues.push({text:item.textContent?.slice(0,70),tag:item.tagName,x:r.x,y:r.y,w:r.width,h:r.height});
   }
   return issues;
  });
  geometry.push({slide:i+1,issues});
  await page.screenshot({path:path.join(dest,`slide-${String(i+1).padStart(2,'0')}.png`)});
 }
 await page.evaluate(()=>{const deck=document.getElementById('deck');deck.style.transition='none';deck.style.transform=`translateX(${-7*innerWidth}px)`;});
 const gifs=page.locator('section.slide').nth(7).locator('img');
 const before=await gifs.nth(0).screenshot();await page.waitForTimeout(1000);const after=await gifs.nth(0).screenshot();
 const result={slides:count,errors,geometry,animatedGifChanges:!before.equals(after)};
 await fs.writeFile(path.join(PROJECT,'validation/browser_review.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({slides:count,pageErrors:errors.length,overflowSlides:geometry.filter(x=>x.issues.length).map(x=>x.slide),animatedGifChanges:result.animatedGifChanges}));
}finally{await browser.close();}
