"use strict";
if(new URLSearchParams(location.search).get('report')==='1')document.documentElement.classList.add('report-export');

let fields = [
  ["internet_users_share_pct", "Internet users (%)"],
  ["telephone_lines_per100", "Landlines / 100"],
  ["broadband_subs_per100", "Broadband / 100"],
  ["mobile_subs_per100", "Mobile / 100"],
];
const palette = {"Africa":"#bd4c43","Asia":"#6b54a3","Europe":"#3476b6","North America":"#d29328","Oceania":"#36a0a8","South America":"#399269","Unclassified":"#68717a"};
const svg = document.querySelector("#chart");
const yearControl = document.querySelector("#year");
const regionControl = document.querySelector("#region");
const bundleControl = document.querySelector("#bundle");
const status = document.querySelector("#status");
const details = document.querySelector("#details");
const matchedControl = document.querySelector("#matched");
const fixedControl = document.querySelector("#fixed");
let data = [];
let matchedCodes = new Set();
let brush = {};
let focusPreset = false;
let pendingBrush = null;

const ns = "http://www.w3.org/2000/svg";
function el(name, attrs = {}, parent = svg) {
  const node = document.createElementNS(ns, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  parent.appendChild(node);
  return node;
}
function fmt(n) { return Number(n).toFixed(1); }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function render() {
  svg.replaceChildren();
  const year = Number(yearControl.value);
  const region = regionControl.value;
  const population = data.filter(d => !matchedControl.checked || matchedCodes.has(d.code));
  const rows = population.filter(d => d.year === year && (region === "all" || d.region === region));
  const allYear = population.filter(d => d.year === year);
  const regions = [...new Set(data.map(d => d.region))].sort();
  const color = Object.fromEntries(regions.map(r => [r, palette[r] || "#68717a"]));
  const W = Math.max(900, Math.round(svg.getBoundingClientRect().width));
  const focusView=focusPreset && document.querySelector('#only-selected').checked;
  const H = 580, left = 90, right = focusView?180:65, top = 82, bottom = 58;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const xs = fields.map((_, i) => left + i * (W - left - right) / (fields.length - 1));
  const domainRows = fixedControl.checked ? population : allYear;
  const focusLimits={internet_users_share_pct:100,telephone_lines_per100:25,broadband_subs_per100:5,mobile_subs_per100:180};
  const max = fields.map(([key]) => focusView?focusLimits[key]:Math.max(...domainRows.map(d => d[key])));
  const y = (d, i) => top + (1 - d[fields[i][0]] / max[i]) * (H - top - bottom);
  const bandColors=['#bd7946','#527d9d','#418f7b'];
  const groupColor=d=>bandColors[adoptionBand(d)];
  const centers=[0,1,2].map(b=>{
    const members=rows.filter(d=>adoptionBand(d)===b);
    return fields.map((_,i)=>members.length?members.reduce((sum,d)=>sum+y(d,i),0)/members.length:0);
  });
  const strength = Number(bundleControl.value) / 100;
  const path=d=>countryCurve(xs,fields.map((_,i)=>y(d,i)),centers[adoptionBand(d)],strength);
  const lines = el("g");
  let selected = 0;
  const selectedNames = [];
  if (focusPreset) {
    for (const [key,lo,hi] of [["internet_users_share_pct",70,100],["broadband_subs_per100",0,5]]) {
      const i=fields.findIndex(f=>f[0]===key);
      brush[key]=[top+(1-hi/max[i])*(H-top-bottom),top+(1-lo/max[i])*(H-top-bottom)];
    }
  }
  for (const d of rows) {
    const matches = fields.every(([key], i) => !brush[key] || (y(d, i) >= brush[key][0] && y(d, i) <= brush[key][1]));
    if (matches) {selected++; selectedNames.push(d.country);}
    if(!matches && document.querySelector('#only-selected').checked)continue;
    const line = el("path", {d: path(d), stroke: groupColor(d), class: `country-line${matches ? "" : " dimmed"}`, "data-code":d.code, "data-values":JSON.stringify(fields.map(([key])=>d[key]))}, lines);
    if(matches && Object.keys(brush).length) {line.style.strokeOpacity=".95";line.style.strokeWidth="2.6";}
    line.addEventListener("mouseenter", () => {
      line.classList.add("active");
      details.textContent = `${d.country} · ${d.region} · ${year} — ` + fields.map(([key, label]) => `${label}: ${fmt(d[key])}`).join(" | ");
    });
    line.addEventListener("mouseleave", () => { line.classList.remove("active"); details.textContent = "Hover a country line to inspect its data."; });
  }
  fields.forEach(([key, label], i) => {
    const x = xs[i];
    el("line", {x1: x, y1: top, x2: x, y2: H-bottom, class: "axis"});
    const title = el("text", {x, y: 36, class: "axis-title", role: "button", tabindex: "0"}); title.textContent = label;
    title.setAttribute("aria-label", `Move ${label} one position to the right`);
    const move = () => { const item=fields.splice(i,1)[0]; fields.splice((i+1)%4,0,item); brush={}; focusPreset=false; render(); };
    title.addEventListener("click",move);
    title.addEventListener("keydown",e=>{if(e.key==="Enter")move();});
    for (let t = 0; t <= 4; t++) {
      const ty = H-bottom - t * (H-top-bottom)/4;
      el("line", {x1: x-5, y1: ty, x2: x+5, y2: ty, class: "tick"});
      const tick = el("text", {x: x-10, y: ty+4, class: "tick-label"}); tick.textContent = fmt(max[i]*t/4);
    }
    if (brush[key]) el("rect", {x: x-14, y: brush[key][0], width: 28, height: brush[key][1]-brush[key][0], class: "brush"});
    const zone = el("rect", {x: x-17, y: top, width: 34, height: H-top-bottom, class: "brush-zone"});
    zone.addEventListener("pointerdown", e => {
      focusPreset=false;
      zone.setPointerCapture(e.pointerId);
      const start = clamp(localY(e), top, H-bottom);
      const preview = el("rect", {x: x-14, y: start, width: 28, height: 0, class: "brush"});
      pendingBrush = {key, start, end: start, preview};
    });
    zone.addEventListener("pointermove", e => {
      if (!pendingBrush || pendingBrush.key !== key) return;
      pendingBrush.end = clamp(localY(e), top, H-bottom);
      const a = Math.min(pendingBrush.start, pendingBrush.end), b = Math.max(pendingBrush.start, pendingBrush.end);
      pendingBrush.preview.setAttribute("y", a);
      pendingBrush.preview.setAttribute("height", b-a);
    });
    zone.addEventListener("pointerup", e => {
      if (!pendingBrush || pendingBrush.key !== key) return;
      const end = clamp(localY(e), top, H-bottom);
      const a = Math.min(pendingBrush.start, end), b = Math.max(pendingBrush.start, end);
      if (b-a < 4) delete brush[key]; else brush[key] = [a,b];
      pendingBrush.preview.remove();
      pendingBrush = null;
      render();
    });
  });
  if(focusView){
    let lastLabelY=top-20;
    const named=rows.filter(d=>d.internet_users_share_pct>=70&&d.broadband_subs_per100<=5).sort((a,b)=>y(a,3)-y(b,3));
    for(const d of named){
      const actual=y(d,3),labelY=Math.max(actual,lastLabelY+18);lastLabelY=labelY;
      el('line',{x1:xs[3]+4,y1:actual,x2:xs[3]+18,y2:labelY,stroke:groupColor(d),'stroke-width':1});
      const name=el('text',{x:xs[3]+22,y:labelY+4,fill:groupColor(d),'font-size':13,'font-weight':700});name.textContent=d.country;
    }
  }
  status.textContent = `${selected} of ${rows.length} countries match filters · ${year} · ${region === "all" ? "all regions" : region}`+(focusView?' · axes fitted to the selected countries':'');
  document.querySelector('#selection-summary').textContent = Object.keys(brush).length ?
    (focusPreset ? 'Adoption ≥70%; fixed broadband ≤5 subscriptions/100. ' : 'Selected countries: ') + selectedNames.sort().join(', ') :
    'Use the focus button to inspect countries whose high adoption coexists with low fixed broadband.';
  document.querySelector('#legend').innerHTML=['Below 40% adoption','40–below 70% adoption','At least 70% adoption'].map((label,i)=>`<span><i style="background:${bandColors[i]}"></i>${label}</span>`).join('');
  const bundleVal = document.querySelector('#bundle-value');
  if (bundleVal) bundleVal.value = `${bundleControl.value}%`;
  else if (bundleControl.nextElementSibling) bundleControl.nextElementSibling.value = `${bundleControl.value}%`;
}

function localY(e) {
  const rect = svg.getBoundingClientRect();
  return (e.clientY - rect.top) * 580 / rect.height;
}

fetch("../data/infovis_countries.json")
  .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
  .then(rows => {
    data = rows;
    const counts = new Map();
    for (const row of data) counts.set(row.code,(counts.get(row.code)||0)+1);
    matchedCodes = new Set([...counts].filter(([,count])=>count===2).map(([code])=>code));
    for (const year of [...new Set(data.map(d => d.year))].sort()) yearControl.add(new Option(year, year));
    for (const region of [...new Set(data.map(d => d.region))].sort()) regionControl.add(new Option(region, region));
    yearControl.value = String(Math.max(...data.map(d => d.year)));
    const params = new URLSearchParams(location.search);
    if(params.has("year") && [...yearControl.options].some(o=>o.value===params.get("year")))yearControl.value=params.get("year");
    if(params.has("bundle"))bundleControl.value=String(clamp(Number(params.get("bundle")),0,100));
    if(params.get("matched")==="1")matchedControl.checked=true;
    if(params.get("fixed")==="1")fixedControl.checked=true;
    yearControl.addEventListener("change", () => { brush = {}; focusPreset=false; render(); });
    regionControl.addEventListener("change", render);
    bundleControl.addEventListener("input", render);
    matchedControl.addEventListener("change",()=>{brush={};render();});
    fixedControl.addEventListener("change",()=>{brush={};render();});
    document.querySelector("#legend").innerHTML=[...new Set(data.map(d=>d.region))].sort()
      .map(r=>`<span><i style="background:${palette[r]||"#68717a"}"></i>${r}</span>`).join("");
    document.querySelector("#clear").addEventListener("click", () => { focusPreset=false; brush = {}; render(); });
    document.querySelector('#focus').addEventListener('click',()=>{focusPreset=true;brush={};yearControl.value='2020';regionControl.value='all';matchedControl.checked=true;fixedControl.checked=true;bundleControl.value=35;render();});
    document.querySelector('#only-selected').addEventListener('change',render);
    if(params.get('context')==='1')document.querySelector('#only-selected').checked=false;
    if(params.get('focus')==='1'){focusPreset=true;yearControl.value='2020';regionControl.value='all';matchedControl.checked=true;fixedControl.checked=true;}
    window.addEventListener("resize", render);
    render();
  })
  .catch(err => { status.textContent = `Could not load data: ${err.message}. Run the preparation script and local server from the project directory.`; });
