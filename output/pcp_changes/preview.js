"use strict";
const base=[['internet_users_share_pct','Internet use',50],['broadband_subs_per100','Fixed broadband',25],['telephone_lines_per100','Landlines',25],['mobile_subs_per100','Mobile',100]];
let fields=[...base],drag=null;const svg=document.querySelector('#chart'),lo=document.querySelector('#lo'),hi=document.querySelector('#hi');
const named={GEO:'#b46a32',UZB:'#168479',BRN:'#7355a4'};
function add(tag,attrs={},parent=svg){let n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);parent.appendChild(n);return n;}
function txt(x,y,s,attrs={}){const n=add('text',{x,y,fill:'#203c50','font-size':14,...attrs});n.textContent=s;return n;}
function render(){
 svg.replaceChildren();let low=Number(lo.value),high=Number(hi.value);if(low>high)[low,high]=[high,low];
 const selected=d=>d.internet_users_share_pct>=low&&d.internet_users_share_pct<=high;
 const groups=[records.filter(d=>!selected(d)),records.filter(selected)];const xs=[110,470,830,1190],top=115,mid=350,bottom=585;
 const y=(d,i)=>mid-d[fields[i][0]]/fields[i][2]*(mid-top);
 const centers=groups.map(g=>fields.map((_,i)=>g.length?g.reduce((s,d)=>s+y(d,i),0)/g.length:mid));
 txt(35,30,`${groups[1].length} selected countries · Gain range: ${low} to ${high} percentage points`,{'font-size':19,'font-weight':700});
 add('rect',{x:55,y:top,width:1310,height:mid-top,fill:'#f4f9f8'});add('rect',{x:55,y:mid,width:1310,height:bottom-mid,fill:'#faf8f5'});
 add('line',{x1:55,x2:1365,y1:mid,y2:mid,stroke:'#657c89','stroke-dasharray':'5 5'});
 const draw=d=>{const on=selected(d),color=on?(named[d.code]||'#628eaa'):'#bdc6cc',focus=on&&named[d.code];
 const path=add('path',{d:countryCurve(xs,fields.map((_,i)=>y(d,i)),centers[+on],Number(document.querySelector('#curves').value)),stroke:color,'stroke-width':focus?2.6:on?1:.65,'stroke-opacity':focus?1:on?.4:.16,class:'line','data-code':d.code});
 path.addEventListener('mouseenter',()=>document.querySelector('#details').textContent=d.country+' — '+base.map(([key,label])=>label+': '+(d[key]>=0?'+':'')+d[key].toFixed(2)).join(' | '));
 if(focus){for(let i=0;i<4;i++)add('circle',{cx:xs[i],cy:y(d,i),r:3.5,fill:color});txt(xs[3]+18,y(d,3)+4,d.country,{fill:color,'font-weight':700});}}
 records.filter(d=>!selected(d)).forEach(draw);records.filter(d=>selected(d)&&!named[d.code]).forEach(draw);records.filter(d=>selected(d)&&named[d.code]).forEach(draw);
 fields.forEach(([key,label,lim],i)=>{
  const x=xs[i];add('line',{x1:x,x2:x,y1:top,y2:bottom,stroke:'#91a5b3'});
  const title=txt(x,75,label,{'text-anchor':'middle','font-weight':700,'font-size':18,class:'axis-title',tabindex:0,role:'button'});
  const move=()=>{const f=fields.splice(i,1)[0];fields.splice((i+1)%4,0,f);render();};title.onclick=move;title.onkeydown=e=>{if(e.key==='Enter')move();};
  txt(x,96,key===base[0][0]?'change in percentage points':'change in subscriptions / 100',{'text-anchor':'middle','font-size':12});
  for(const t of [-1,-.5,0,.5,1]){const yy=mid-t*(mid-top);add('line',{x1:x-5,x2:x+5,y1:yy,y2:yy,stroke:'#91a5b3'});txt(x-10,yy+4,(t>0?'+':'')+(t*lim),{'text-anchor':'end','paint-order':'stroke',stroke:'white','stroke-width':4,'stroke-linejoin':'round'});}
  if(key===base[0][0]){
   add('rect',{x:x-9,y:mid-high/lim*(mid-top),width:18,height:(high-low)/lim*(mid-top),fill:'#d7eaf4',stroke:'#4989ac'});
   const z=add('rect',{x:x-18,y:top,width:36,height:bottom-top,class:'brush-zone'});
   const value=e=>{let point=svg.createSVGPoint();point.x=e.clientX;point.y=e.clientY;point=point.matrixTransform(svg.getScreenCTM().inverse());return Math.max(-lim,Math.min(lim,(mid-point.y)/(mid-top)*lim));};
   z.onpointerdown=e=>{z.setPointerCapture(e.pointerId);drag=value(e);};z.onpointerup=e=>{if(drag===null)return;const end=value(e);lo.value=Math.round(Math.min(drag,end));hi.value=Math.round(Math.max(drag,end));drag=null;render();};
  }
 });
 txt(55,635,'Above zero = increase. Below zero = decrease. Axis ranges differ; read the labelled values.');
 svg.dataset.selected=groups[1].length;
}
for(const el of [lo,hi,document.querySelector('#curves')])el.onchange=render;
document.querySelector('#reorder').onclick=()=>{fields.push(fields.shift());render();};
document.querySelector('#reset').onclick=()=>{fields=[...base];lo.value=20;hi.value=30;document.querySelector('#curves').value='.2';document.querySelector('#curves').value='0.2';render();};render();
