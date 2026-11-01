"use strict";
const svg = d3.select("#network"), W=1100, H=700, margin=55;
svg.attr("viewBox", `0 0 ${W} ${H}`);
const canvas=svg.append("g"), links=canvas.append("g"), nodes=canvas.append("g");
const matrixG=canvas.append("g").style("display","none");
const mDiag=matrixG.append("g"), mCells=matrixG.append("g"), mLabels=matrixG.append("g"), mHover=matrixG.append("g").style("pointer-events","none");
const zoom=d3.zoom().scaleExtent([.5,8]).on("zoom",e=>canvas.attr("transform",e.transform));
svg.call(zoom);
const layoutBox=document.querySelector("#layout"), similarityBox=document.querySelector("#similarity");
const viewBox=document.querySelector("#view"), orderBox=document.querySelector("#matrix-order");
const orderLabel=document.querySelector("#order-label");
const regionBox=document.querySelector("#node-region"), hideIsolates=document.querySelector("#hide-isolates");
const searchBox=document.querySelector("#search"), status=document.querySelector("#status"), details=document.querySelector("#details");
const colors=d3.scaleOrdinal().domain(["Africa","Asia","Europe","North America","Oceania","South America","Unclassified"])
  .range(["#bd4c43","#6b54a3","#3476b6","#d29328","#36a0a8","#399269","#68717a"]);
let payload, selected=null, hoverCell=null;
function visibleState(){
  const threshold=Number(similarityBox.value);
  const byId=new Map(payload.nodes.map(n=>[n.id,n]));
  const regionNodes=payload.nodes.filter(n=>regionBox.value==='all'||n.region===regionBox.value);
  const allowed=new Set(regionNodes.map(n=>n.id));
  const visible=payload.all_edges.filter(e=>e.similarity>=threshold&&allowed.has(e.source)&&allowed.has(e.target));
  const degree=new Map(regionNodes.map(n=>[n.id,0]));
  for(const e of visible){degree.set(e.source,degree.get(e.source)+1);degree.set(e.target,degree.get(e.target)+1);}
  const displayed=regionNodes.filter(n=>!hideIsolates.checked||degree.get(n.id)>0);
  return {threshold,byId,allowed,visible,degree,displayed};
}
function pairKey(a,b){return a<b?a+'|'+b:b+'|'+a;}
let pairSim=new Map();
function render() {
  if(viewBox.value==='matrix'){renderMatrix();return;}
  const {threshold,byId,visible,degree,displayed}=visibleState();
  const pos=payload.layouts[layoutBox.value];
  if(selected&&!displayed.some(n=>n.id===selected))selected=null;
  const neighbor=new Set(selected?[selected]:[]);
  if(selected) for(const e of visible) {
    if(e.source===selected) neighbor.add(e.target);
    if(e.target===selected) neighbor.add(e.source);
  }
  const X=id=>margin+pos[id][0]*(W-2*margin), Y=id=>margin+pos[id][1]*(H-2*margin);
  links.selectAll("line").data(visible,e=>`${e.source}-${e.target}`).join("line")
    .attr("x1",e=>X(e.source)).attr("y1",e=>Y(e.source))
    .attr("x2",e=>X(e.target)).attr("y2",e=>Y(e.target))
    .attr("stroke","#71879b").attr("stroke-width",e=>.45+1.2*e.similarity)
    .attr("stroke-opacity",e=>selected?((e.source===selected||e.target===selected) ? 0.7 : 0.035):0.17);
  const circles=nodes.selectAll("circle").data(displayed,n=>n.id).join("circle")
    .attr("cx",n=>X(n.id)).attr("cy",n=>Y(n.id))
    .attr("r",n=>Math.sqrt(9+2*degree.get(n.id))).attr("fill",n=>colors(n.region))
    .attr("stroke",n=>n.id===selected?"#142b3f":"white")
    .attr("stroke-width",n=>n.id===selected?2:.65)
    .attr("opacity",n=>selected?(neighbor.has(n.id)?1:.17):.9)
    .attr("tabindex",0).attr("role","button")
    .attr("aria-label",n=>`${n.country}, ${n.region}, ${degree.get(n.id)} visible derived links`)
    .on("click",(event,n)=>{selected=n.id; render();})
    .on("keydown",(event,n)=>{if(event.key==="Enter"){selected=n.id;render();}});
  circles.selectAll("title").data(n=>[n]).join("title").text(n=>`${n.country} (${n.id})`);
  nodes.selectAll("text").data(selected?[byId.get(selected)]:[],n=>n.id).join("text")
    .attr("x",n=>X(n.id)+11).attr("y",n=>Y(n.id)+4)
    .attr("font-size",14).attr("font-weight",700).attr("fill","#142b3f").text(n=>n.country);
  status.textContent=`${displayed.length} of ${payload.nodes.length} countries · ${visible.length} of ${payload.all_edges.length} pairwise similarities visible · ${layoutBox.value} layout`;
  document.querySelector("#similarity-value").value=threshold.toFixed(6);
  similarityBox.setAttribute('aria-valuetext',threshold.toFixed(6));
  if(selected){
    const n=byId.get(selected);
    details.textContent=`${n.country} (${n.id}) · ${n.region} · Internet ${n.internet_pct.toFixed(1)}% · Mobile ${n.mobile_per100.toFixed(1)}/100 · Broadband ${n.broadband_per100.toFixed(1)}/100 · Landline ${n.landlines_per100.toFixed(1)}/100 · ${neighbor.size-1} visible neighbors`;
  } else details.textContent="Click a country to see its profile and linked neighbors. Drag to pan; scroll to zoom.";
}
const MAT={left:152,top:128};
const short=s=>s.length>20?s.slice(0,19)+'…':s;
function renderMatrix(){
  const {threshold,byId,visible,degree,displayed}=visibleState();
  if(selected&&!displayed.some(n=>n.id===selected))selected=null;
  let ids;
  if(orderBox.value==='name')ids=[...displayed].sort((a,b)=>byId.get(a).country.localeCompare(byId.get(b).country));
  else if(orderBox.value==='degree')ids=[...displayed].sort((a,b)=>degree.get(b.id)-degree.get(a.id)||byId.get(a.id).country.localeCompare(byId.get(b.id).country));
  else ids=[...displayed].sort((a,b)=>String(byId.get(a.id).region).localeCompare(String(byId.get(b.id).region))||byId.get(a.id).country.localeCompare(byId.get(b.id).country));
  ids=ids.map(n=>n.id);
  const index=new Map(ids.map((id,i)=>[id,i]));
  const nL=Math.max(ids.length,1);
  const cell=Math.min((W-MAT.left-16)/nL,(H-MAT.top-16)/nL);
  const fill=d3.interpolateLab('#dff3f3','#0d5464');
  const cellColor=s=>fill(Math.min(1,(s-threshold)/Math.max(1e-9,1-threshold)));
  const neighborsOf=selected?(new Set([selected])):(new Set());
  if(selected)for(const e of visible){if(e.source===selected)neighborsOf.add(e.target);if(e.target===selected)neighborsOf.add(e.source);}
  // One rect per retained pair, drawn on both sides of the diagonal.
  const data=[];
  for(const e of visible){
    const i=index.get(e.source),j=index.get(e.target);
    if(i===undefined||j===undefined)continue;
    data.push({i,j,s:e.similarity});data.push({i:j,j:i,s:e.similarity});
  }
  mCells.selectAll("rect").data(data,d=>`${d.i}-${d.j}`).join("rect")
    .attr("x",d=>MAT.left+d.j*cell).attr("y",d=>MAT.top+d.i*cell)
    .attr("width",cell).attr("height",cell)
    .attr("fill",d=>cellColor(d.s))
    .attr("shape-rendering","crispEdges");
  mDiag.selectAll("rect").data(ids,d=>d).join("rect")
    .attr("x",d=>MAT.left+index.get(d)*cell).attr("y",d=>MAT.top+index.get(d)*cell)
    .attr("width",cell).attr("height",cell).attr("fill","#a9b3ba").attr("shape-rendering","crispEdges");
  const fs=Math.max(6,Math.min(11,cell*.9));
  mLabels.selectAll("text.row").data(ids,d=>d).join("text")
    .attr("class","row").attr("x",MAT.left-4).attr("y",d=>MAT.top+(index.get(d)+.5)*cell)
    .attr("dy",".32em").attr("text-anchor","end").attr("font-size",fs)
    .attr("fill",d=>colors(byId.get(d).region)).attr("cursor","pointer")
    .text(d=>short(byId.get(d).country))
    .each(function(d){d3.select(this).selectAll("title").data([d]).join("title").text(()=>byId.get(d).country);})
    .on("click",(event,d)=>{selected=d;render();});
  mLabels.selectAll("text.col").data(ids,d=>d).join("text")
    .attr("class","col").attr("transform",d=>`translate(${MAT.left+(index.get(d)+1)*cell},${MAT.top-4}) rotate(-90)`)
    .attr("x",0).attr("y",0).attr("dy",".28em").attr("font-size",fs)
    .attr("fill",d=>colors(byId.get(d).region)).text(d=>short(byId.get(d).country))
    .each(function(d){d3.select(this).selectAll("title").data([d]).join("title").text(()=>byId.get(d).country);});
  // Hover crosshair: transparent overlay derives row/col without per-cell hit targets.
  let overlay=matrixG.select("rect.overlay");
  if(overlay.empty())overlay=matrixG.append("rect").attr("class","overlay").attr("fill","transparent");
  overlay.attr("x",MAT.left).attr("y",MAT.top).attr("width",nL*cell).attr("height",nL*cell)
    .on("mousemove",(event)=>{
      const p=d3.pointer(event,matrixG.select("rect.overlay").node());
      const i=Math.floor((p[1]-MAT.top)/cell),j=Math.floor((p[0]-MAT.left)/cell);
      if(i<0||j<0||i>=nL||j>=nL){mHover.selectAll("rect").remove();hoverCell=null;return;}
      hoverCell={i,j};
      mHover.selectAll("rect").data([i,ids.length+j]).join("rect")
        .attr("x",d=>MAT.left+(d>=ids.length?d-ids.length:0)*cell)
        .attr("y",d=>MAT.top+(d<ids.length?d:0)*cell)
        .attr("width",d=>d<ids.length?nL*cell:cell)
        .attr("height",d=>d<ids.length?cell:nL*cell)
        .attr("fill","none").attr("stroke","#142b3f").attr("stroke-opacity",.45)
        .attr("shape-rendering","crispEdges").attr("stroke-width",.6);
      const a=byId.get(ids[i]),b=byId.get(ids[j]);
      const sim=pairSim.get(pairKey(ids[i],ids[j]));
      details.textContent=ids[i]===ids[j]?`${a.country} self-cell (diagonal excluded).`
        :`${a.country} – ${b.country}: measured similarity ${sim.toFixed(3)} — ${sim>=threshold?`retained at cutoff ${threshold.toFixed(3)}`:`below cutoff ${threshold.toFixed(3)}`}`;
    })
    .on("click",()=>{if(hoverCell){selected=ids[hoverCell.i];render();}}).on("mouseleave",()=>{mHover.selectAll("rect").remove();hoverCell=null;if(!selected)details.textContent="Hover a cell to inspect a pair; click a row label or use Find country to select one. Drag to pan; scroll to zoom.";});
  if(selected){
    const i=index.get(selected);
    if(i!==undefined)mHover.selectAll("rect.select").data(["sel-row","sel-col"]).join("rect")
      .attr("class","select")
      .attr("x",d=>d==="sel-row"?MAT.left:MAT.left+i*cell)
      .attr("y",d=>d==="sel-row"?MAT.top+i*cell:MAT.top)
      .attr("width",d=>d==="sel-row"?nL*cell:cell)
      .attr("height",d=>d==="sel-row"?cell:nL*cell)
      .attr("fill","none").attr("stroke","#142b3f").attr("stroke-width",1.1)
      .attr("shape-rendering","crispEdges");
  }
  status.textContent=`${displayed.length} of ${payload.nodes.length} countries · ${visible.length} of ${payload.all_edges.length} pairwise similarities visible · adjacency matrix · ${orderBox.value} order`;
  document.querySelector("#similarity-value").value=threshold.toFixed(6);
  similarityBox.setAttribute('aria-valuetext',threshold.toFixed(6));
  if(selected){
    const node=byId.get(selected);
    details.textContent=`${node.country} (${node.id}) · ${node.region} · Internet ${node.internet_pct.toFixed(1)}% · Mobile ${node.mobile_per100.toFixed(1)}/100 · Broadband ${node.broadband_per100.toFixed(1)}/100 · Landline ${node.landlines_per100.toFixed(1)}/100 · ${neighborsOf.size-1} visible neighbors`;
  } else details.textContent="Hover a cell to inspect a pair; click a row label or use Find country to select one. Drag to pan; scroll to zoom.";
}
function findCountry(){
  const q=searchBox.value.trim().toLowerCase();
  const n=payload.nodes.find(n=>n.id.toLowerCase()===q||n.country.toLowerCase()===q)
    ||payload.nodes.find(n=>n.country.toLowerCase().includes(q)&&q);
  if(n){regionBox.value='all';hideIsolates.checked=false;selected=n.id;render();} else if(q)details.textContent=`No country matches “${searchBox.value}”.`;
}
fetch("../data/country_network_2020.json").then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(data=>{
  payload=data;
  pairSim=new Map(data.all_edges.map(e=>[pairKey(e.source,e.target),e.similarity]));
  similarityBox.value=data.default_threshold;
  for(const name of Object.keys(data.layouts)) layoutBox.add(new Option(name,name));
  for(const n of data.nodes) document.querySelector("#countries").append(new Option(n.country,n.country));
  for(const region of [...new Set(data.nodes.map(n=>n.region))].sort())regionBox.add(new Option(region,region));
  document.querySelector("#legend").innerHTML=colors.domain().map(r=>`<span><i style="background:${colors(r)}"></i>${r}</span>`).join("")+`<span>Node-link: node area = visible degree + minimum marker size; outline = selection. Matrix: cell color = retained pair similarity; gray diagonal excluded; scan order groups regions or sorts by degree/name</span>`;
  layoutBox.addEventListener("change",render); similarityBox.addEventListener("input",render);
  regionBox.addEventListener('change',render);hideIsolates.addEventListener('change',render);
  orderBox.addEventListener('change',render);
  const applyView=()=>{
    const isM=viewBox.value==='matrix';
    links.style('display',isM?'none':null);nodes.style('display',isM?'none':null);
    matrixG.style('display',isM?null:'none');orderLabel.style.display=isM?'':'none';
    layoutBox.disabled=isM;
    svg.attr('aria-label',isM?'Interactive country similarity adjacency matrix':'Interactive country similarity network with three layouts');
    svg.transition().duration(250).call(zoom.transform,d3.zoomIdentity);
    render();
  };
  viewBox.addEventListener('change',applyView);
  const params=new URLSearchParams(location.search);
  if(params.get('view')==='matrix')viewBox.value='matrix';
  applyView();
  if(params.get('find')){searchBox.value=params.get('find');findCountry();}
  // Preserve the exact P95 default while allowing useful keyboard increments.
  similarityBox.addEventListener('keydown',event=>{
    const changes={ArrowLeft:-.005,ArrowDown:-.005,ArrowRight:.005,ArrowUp:.005};
    if(event.key in changes||event.key==='Home'||event.key==='End'){
      event.preventDefault();
      similarityBox.value=event.key==='Home'?0:event.key==='End'?1:Math.max(0,Math.min(1,Number(similarityBox.value)+changes[event.key]));
      render();
    }
  });
  document.querySelector("#find").addEventListener("click",findCountry);
  searchBox.addEventListener("keydown",e=>{if(e.key==="Enter")findCountry();});
  document.querySelector("#reset").addEventListener("click",()=>{selected=null;similarityBox.value=payload.default_threshold;regionBox.value='all';hideIsolates.checked=false;searchBox.value="";orderBox.value='region';svg.transition().duration(350).call(zoom.transform,d3.zoomIdentity);render();});
}).catch(e=>status.textContent=`Could not load network data: ${e.message}`);
