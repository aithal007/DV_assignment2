"use strict";
const svg = d3.select("#network"), W=1100, H=700, margin=55;
svg.attr("viewBox", `0 0 ${W} ${H}`);
const canvas=svg.append("g"), links=canvas.append("g"), nodes=canvas.append("g");
const zoom=d3.zoom().scaleExtent([.5,8]).on("zoom",e=>canvas.attr("transform",e.transform));
svg.call(zoom);
const layoutBox=document.querySelector("#layout"), similarityBox=document.querySelector("#similarity");
const regionBox=document.querySelector("#node-region"), hideIsolates=document.querySelector("#hide-isolates");
const searchBox=document.querySelector("#search"), status=document.querySelector("#status"), details=document.querySelector("#details");
const colors=d3.scaleOrdinal().domain(["Africa","Asia","Europe","North America","Oceania","South America","Unclassified"])
  .range(["#bd4c43","#6b54a3","#3476b6","#d29328","#36a0a8","#399269","#68717a"]);
let payload, selected=null;
function render() {
  const pos=payload.layouts[layoutBox.value], threshold=Number(similarityBox.value);
  const byId=new Map(payload.nodes.map(n=>[n.id,n]));
  const regionNodes=payload.nodes.filter(n=>regionBox.value==='all'||n.region===regionBox.value);
  const allowed=new Set(regionNodes.map(n=>n.id));
  const visible=payload.all_edges.filter(e=>e.similarity>=threshold&&allowed.has(e.source)&&allowed.has(e.target));
  const visibleDegree=new Map(payload.nodes.map(n=>[n.id,0]));
  for(const e of visible){visibleDegree.set(e.source,visibleDegree.get(e.source)+1);visibleDegree.set(e.target,visibleDegree.get(e.target)+1);}
  const displayed=regionNodes.filter(n=>!hideIsolates.checked||visibleDegree.get(n.id)>0);
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
    .attr("r",n=>n.id===selected?8:4.6).attr("fill",n=>colors(n.region))
    .attr("stroke",n=>n.id===selected?"#142b3f":"white")
    .attr("stroke-width",n=>n.id===selected?2:.65)
    .attr("opacity",n=>selected?(neighbor.has(n.id)?1:.17):.9)
    .attr("tabindex",0).attr("role","button")
    .attr("aria-label",n=>`${n.country}, ${n.region}, ${visibleDegree.get(n.id)} visible derived links`)
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
function findCountry(){
  const q=searchBox.value.trim().toLowerCase();
  const n=payload.nodes.find(n=>n.id.toLowerCase()===q||n.country.toLowerCase()===q)
    ||payload.nodes.find(n=>n.country.toLowerCase().includes(q)&&q);
  if(n){regionBox.value='all';hideIsolates.checked=false;selected=n.id;render();} else if(q)details.textContent=`No country matches “${searchBox.value}”.`;
}
fetch("../data/country_network_2020.json").then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(data=>{
  payload=data;
  similarityBox.value=data.default_threshold;
  for(const name of Object.keys(data.layouts)) layoutBox.add(new Option(name,name));
  for(const n of data.nodes) document.querySelector("#countries").append(new Option(n.country,n.country));
  for(const region of [...new Set(data.nodes.map(n=>n.region))].sort())regionBox.add(new Option(region,region));
  document.querySelector("#legend").innerHTML=colors.domain().map(r=>`<span><i style="background:${colors(r)}"></i>${r}</span>`).join("");
  layoutBox.addEventListener("change",render); similarityBox.addEventListener("input",render);
  regionBox.addEventListener('change',render);hideIsolates.addEventListener('change',render);
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
  document.querySelector("#reset").addEventListener("click",()=>{selected=null;similarityBox.value=payload.default_threshold;regionBox.value='all';hideIsolates.checked=false;searchBox.value="";svg.transition().duration(350).call(zoom.transform,d3.zoomIdentity);render();});
  render();
}).catch(e=>status.textContent=`Could not load network data: ${e.message}`);
