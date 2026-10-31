"use strict";
if(new URLSearchParams(location.search).get('report')==='1')document.documentElement.classList.add('report-export');
const svg=d3.select("#treemap"), W=1100,H=690;
svg.attr("viewBox",`0 0 ${W} ${H}`);
const status=document.querySelector("#status"), details=document.querySelector("#details");
const hierarchyBox=document.querySelector("#hierarchy"), back=document.querySelector("#back");
const tilingBox=document.querySelector('#tiling');
const fmt=d3.format(",.0f"), pct=d3.format(".1f");
let records=[], root, current;
function band(v){return v<25?"Under 25%":v<50?"25–<50%":v<75?"50–<75%":"75–100%";}
function build(preserveZoom=false){
  const previous=preserveZoom&&current?current.ancestors().reverse().slice(1).map(n=>n.data.name):[];
  const mode=hierarchyBox.value, groups=new Map();
  for(const r of records){
    const keys=mode==="region"?[r.region]:[band(r.internet_pct),r.region];
    let level=groups;
    for(const key of keys){if(!level.has(key))level.set(key,{name:key,children:new Map()});level=level.get(key).children;}
    level.set(r.code,{name:r.country,code:r.code,value:r.internet_users,adoption:r.internet_pct});
  }
  const convert=map=>[...map.values()].map(d=>d.children?{name:d.name,children:convert(d.children)}:d);
  root=d3.hierarchy({name:"Included countries",children:convert(groups)})
    .sum(d=>d.children?0:(d.value||0)).sort((a,b)=>b.value-a.value);
  d3.treemap().tile(tilingBox.value==='slice-dice'?d3.treemapSliceDice:d3.treemapSquarify).size([W,H]).paddingInner(2).paddingOuter(2).paddingTop(d=>d.depth>0&&d.children?44:2)(root);
  current=root;
  const zoom=previous.length?previous.join('/'):new URLSearchParams(location.search).get("zoom");
  if(zoom){
    const path=zoom.split("/");
    for(const name of path){
      const next=current.children?.find(node=>node.data.name===name);
      if(!next)break;
      current=next;
    }
  }
  render();
}
function render(){
  svg.selectAll("*").remove();
  const children=current.children||[];
  const X=d3.scaleLinear().domain([current.x0,current.x1]).range([0,W]);
  const Y=d3.scaleLinear().domain([current.y0,current.y1]).range([0,H]);
  const tile=svg.selectAll("g.tile").data(children).join("g").attr("class","tile")
    .attr("transform",d=>`translate(${X(d.x0)},${Y(d.y0)})`)
    .attr("role","button").attr("tabindex",0)
    .attr("aria-label",d=>`${d.data.name}, ${fmt(d.value)} internet users${d.children?", zoom in":""}`)
    .on("click",(e,d)=>{if(d.children){current=d;render();}else show(d);})
    .on("keydown",(e,d)=>{if(e.key==="Enter"){if(d.children){current=d;render();}else show(d);}})
    .on("mouseenter",(e,d)=>show(d));
  svg.on("mouseleave",()=>{details.textContent="Click a group to zoom in. Hover a rectangle to see its values.";});
  tile.append("rect").attr("width",d=>Math.max(0,X(d.x1)-X(d.x0)))
    .attr("height",d=>Math.max(0,Y(d.y1)-Y(d.y0)))
    .attr("fill",d=>d.children?"#dce8f2":d3.interpolateViridis(d.data.adoption/100))
    .attr("stroke","white").attr("stroke-width",1);
  tile.filter(d=>d.children).each(function(parent){
    const preview=d3.select(this).append('g').attr('pointer-events','none');
    for(const leaf of parent.leaves()){
      const x=X(leaf.x0)-X(parent.x0), y=Y(leaf.y0)-Y(parent.y0);
      const w=Math.max(0,X(leaf.x1)-X(leaf.x0)),h=Math.max(0,Y(leaf.y1)-Y(leaf.y0));
      preview.append('rect').attr('x',x).attr('y',y).attr('width',w).attr('height',h)
        .attr('fill',d3.interpolateViridis(leaf.data.adoption/100)).attr('stroke','white').attr('stroke-width',.6);
      if(w>leaf.data.name.length*5.7+10&&h>18)preview.append('text').attr('x',x+4).attr('y',y+13)
        .attr('font-size',10).attr('fill',leaf.data.adoption<55?'white':'#142b3f').text(leaf.data.name);
    }
  });
  tile.append("text").attr("x",8).attr("y",17).attr("font-size",d=>d.children?15:12)
    .attr("font-weight",d=>d.children?700:500).attr("fill",d=>d.children?"#15324a":d.data.adoption<55?"#fff":"#15283b")
    .attr("pointer-events","none")
    .text(d=>X(d.x1)-X(d.x0)>d.data.name.length*7+14 && Y(d.y1)-Y(d.y0)>23?d.data.name:"");
  tile.append("title").text(d=>`${d.data.name}: ${fmt(d.value)} internet users`);
  tile.filter(d=>d.children).append('text').attr('x',8).attr('y',39)
    .attr('font-size',14).attr('fill','#15324a').attr('pointer-events','none')
    .text(d=>X(d.x1)-X(d.x0)>165 && Y(d.y1)-Y(d.y0)>52 ? `${pct(100*d.value/root.value)}% of total · ${d.leaves().length} countries` : '');
  const chain=current.ancestors().reverse().map(d=>d.data.name);
  document.querySelector("#crumb").textContent=chain.join(" / ");
  back.disabled=!current.parent;
  status.textContent=`${fmt(current.value)} internet users in ${current.data.name} · ${children.length} visible groups/countries · ${tilingBox.selectedOptions[0].textContent}`;
}
function show(d){
  details.textContent=d.children?`${d.data.name}: ${fmt(d.value)} internet users across ${d.leaves().length} countries. Click to zoom.`:
    `${d.data.name}: ${fmt(d.value)} internet users (${pct(100*d.value/d.parent.value)}% of ${d.parent.data.name}); ${pct(d.data.adoption)}% of people use the internet.`;
}
fetch("../data/treemap_countries_2020.json").then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(data=>{
  records=data.countries;
  if(new URLSearchParams(location.search).get("hierarchy")==="adoption")hierarchyBox.value="adoption";
  hierarchyBox.addEventListener("change",()=>build(false));
  tilingBox.addEventListener('change',()=>build(true));
  back.addEventListener("click",()=>{if(current.parent){current=current.parent;render();}});
  build();
}).catch(e=>status.textContent=`Could not load treemap data: ${e.message}`);
